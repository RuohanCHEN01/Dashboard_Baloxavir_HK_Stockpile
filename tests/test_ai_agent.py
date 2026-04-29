"""Tests for AI Agent module."""

import pytest
from unittest.mock import MagicMock, patch
from ai_agent.llm_interface import LLMClient, PROVIDER_REGISTRY, MODEL_ALIASES
from ai_agent.literature_extractor import LiteratureExtractor, ExtractedParams
from ai_agent.nl_query import NLQueryEngine
from ai_agent.report_generator import PolicyReportGenerator


class TestLLMClient:
    """Test suite for LLMClient."""

    def test_provider_registry_has_all_providers(self):
        """All expected providers should be registered."""
        expected = {"openai", "claude", "mimo", "deepseek"}
        assert expected.issubset(set(PROVIDER_REGISTRY.keys()))

    def test_invalid_provider_raises_error(self):
        """Invalid provider name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMClient(provider="nonexistent_provider")

    def test_client_info_returns_correct_fields(self):
        """info property should return expected keys."""
        client = LLMClient(provider="mimo")
        info = client.info
        assert info["provider"] == "mimo"
        assert info["model"] == "MiMo-V2.5-Pro"
        assert info["context_window"] == 1_000_000
        assert info["supports_vision"] is True

    def test_client_repr(self):
        """Client should have a readable repr."""
        client = LLMClient(provider="openai")
        assert "openai" in repr(client)

    def test_mimo_has_largest_context_window(self):
        """MiMo V2.5-Pro should have 1M context window."""
        mimo_config = PROVIDER_REGISTRY["mimo"]
        assert mimo_config.context_window == 1_000_000

    def test_deepseek_no_vision(self):
        """DeepSeek should not support vision."""
        ds_config = PROVIDER_REGISTRY["deepseek"]
        assert ds_config.supports_vision is False


class TestExtractedParams:
    """Test suite for ExtractedParams dataclass."""

    def test_default_values_are_none(self):
        """Default params should be None/empty."""
        params = ExtractedParams()
        assert params.vaccine_efficacy is None
        assert params.confidence == "low"
        assert params.source_citation == ""

    def test_to_dict_excludes_none(self):
        """to_dict should exclude None values."""
        params = ExtractedParams(
            vaccine_efficacy=0.42,
            confidence="high",
            source_citation="Test et al. 2026",
            serial_interval=None,  # Should be excluded
        )
        d = params.to_dict()
        assert "vaccine_efficacy" in d
        assert "serial_interval" not in d
        assert d["vaccine_efficacy"] == 0.42

    def test_to_json_is_valid_json(self):
        """to_json should produce valid JSON string."""
        import json
        params = ExtractedParams(
            vaccine_efficacy=0.42,
            confidence="high",
            source_citation="Test 2026",
        )
        result = json.loads(params.to_json())
        assert result["vaccine_efficacy"] == 0.42


class TestLiteratureExtractor:
    """Test suite for LiteratureExtractor."""

    def test_extraction_returns_extracted_params(self):
        """extract should return ExtractedParams instance."""
        mock_client = MagicMock(spec=LLMClient)
        extractor = LiteratureExtractor(mock_client)

        mock_client.extract_from_text.return_value = {
            "vaccine_efficacy": 0.42,
            "resistance_frequency": 0.035,
            "confidence": "high",
            "source_citation": "PubMed Abstract",
        }

        result = extractor.extract("VE was 42%...", source_name="Test Paper")
        assert isinstance(result, ExtractedParams)
        assert result.vaccine_efficacy == 0.42
        assert result.confidence == "high"

    def test_extraction_handles_errors_gracefully(self):
        """Failed extraction should return low-confidence params."""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.extract_from_text.side_effect = RuntimeError("API error")
        extractor = LiteratureExtractor(mock_client)

        result = extractor.extract("some text", source_name="Test")
        assert isinstance(result, ExtractedParams)
        assert result.confidence == "low"
        assert "Extraction failed" in result.notes


class TestNLQueryEngine:
    """Test suite for NLQueryEngine."""

    def test_query_without_results_returns_error(self):
        """Query without loaded results should return error message."""
        mock_client = MagicMock(spec=LLMClient)
        engine = NLQueryEngine(mock_client)

        result = engine.query("What is the ICER?")
        assert "No scenario results loaded" in result["answer"]
        assert result["confidence"] == "none"

    def test_load_results_stores_data(self):
        """load_results should store results in cache."""
        mock_client = MagicMock(spec=LLMClient)
        engine = NLQueryEngine(mock_client)

        test_results = [
            {"scenario_name": "BXM_30pct", "icer": 15000, "total_cost": 5000000},
            {"scenario_name": "OTV_30pct", "icer": 22000, "total_cost": 3200000},
        ]
        engine.load_results(test_results)
        assert len(engine._results_cache) == 2

    def test_relevant_scenarios_found_by_keywords(self):
        """_find_relevant_scenarios should match by keyword."""
        mock_client = MagicMock(spec=LLMClient)
        engine = NLQueryEngine(mock_client)

        engine.load_results([
            {"scenario_name": "BXM_30pct_coverage", "icer": 15000},
            {"scenario_name": "OTV_baseline", "icer": 22000},
        ])

        relevant = engine._find_relevant_scenarios("What is the ICER for BXM 30pct coverage?")
        assert "BXM_30pct_coverage" in relevant


class TestPolicyReportGenerator:
    """Test suite for PolicyReportGenerator."""

    def test_generate_section_returns_string(self):
        """generate_section should return a string."""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.complete.return_value = "This is a summary."
        gen = PolicyReportGenerator(mock_client)

        result = gen.generate_section(
            "executive_summary",
            {"icer": 15000, "qaly": 0.05},
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_invalid_section_raises_error(self):
        """Invalid section name should raise ValueError."""
        mock_client = MagicMock(spec=LLMClient)
        gen = PolicyReportGenerator(mock_client)

        with pytest.raises(ValueError, match="Unknown section"):
            gen.generate_section("nonexistent_section", {})

    def test_to_markdown_includes_title(self):
        """Markdown output should include report title."""
        mock_client = MagicMock(spec=LLMClient)
        gen = PolicyReportGenerator(mock_client)

        report = {
            "metadata": {"title": "Test Report", "date": "2026-01-01", "author": "Test"},
            "sections": {"executive_summary": "Summary content."},
        }

        md = gen.to_markdown(report)
        assert "Test Report" in md
        assert "Summary content." in md
