"""
Literature Evidence Extraction Agent.

Extracts structured epidemiological parameters from scientific literature
(PubMed abstracts, WHO guidelines, technical assessment reports) using LLM.
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional

from .llm_interface import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class ExtractedParams:
    """Structured output for extracted epidemiological parameters."""

    vaccine_efficacy: Optional[float] = None
    vaccine_efficacy_ci_low: Optional[float] = None
    vaccine_efficacy_ci_high: Optional[float] = None
    resistance_frequency: Optional[float] = None
    serial_interval: Optional[float] = None
    r0_low: Optional[float] = None
    r0_mid: Optional[float] = None
    r0_high: Optional[float] = None
    symptomatic_proportion: Optional[float] = None
    hospitalization_rate: Optional[float] = None
    icu_rate: Optional[float] = None
    case_fatality_rate: Optional[float] = None
    cost_per_course_bxm_hkd: Optional[float] = None
    cost_per_course_otv_hkd: Optional[float] = None
    confidence: str = "low"
    source_citation: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None and v != ""}

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


# JSON Schema for structured extraction
PARAMS_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "vaccine_efficacy": {
            "type": ["number", "null"],
            "description": "Vaccine effectiveness (VE) as a decimal (e.g., 0.42 for 42%)",
        },
        "vaccine_efficacy_ci_low": {
            "type": ["number", "null"],
            "description": "Lower bound of VE confidence interval",
        },
        "vaccine_efficacy_ci_high": {
            "type": ["number", "null"],
            "description": "Upper bound of VE confidence interval",
        },
        "resistance_frequency": {
            "type": ["number", "null"],
            "description": "Antiviral resistance gene frequency (e.g., 0.035 for 3.5%)",
        },
        "serial_interval": {
            "type": ["number", "null"],
            "description": "Serial interval in days",
        },
        "r0_low": {"type": ["number", "null"], "description": "Low estimate of R0"},
        "r0_mid": {
            "type": ["number", "null"],
            "description": "Point estimate of R0",
        },
        "r0_high": {"type": ["number", "null"], "description": "High estimate of R0"},
        "symptomatic_proportion": {
            "type": ["number", "null"],
            "description": "Proportion of infections that are symptomatic",
        },
        "hospitalization_rate": {
            "type": ["number", "null"],
            "description": "Hospitalization rate per infection",
        },
        "icu_rate": {
            "type": ["number", "null"],
            "description": "ICU admission rate per infection",
        },
        "case_fatality_rate": {
            "type": ["number", "null"],
            "description": "Case fatality rate (CFR)",
        },
        "cost_per_course_bxm_hkd": {
            "type": ["number", "null"],
            "description": "Cost per treatment course of Baloxavir (BXM) in HKD",
        },
        "cost_per_course_otv_hkd": {
            "type": ["number", "null"],
            "description": "Cost per treatment course of Oseltamivir (OTV) in HKD",
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Overall confidence in the extracted values",
        },
        "source_citation": {
            "type": "string",
            "description": "Author/year or title of the source document",
        },
        "notes": {
            "type": "string",
            "description": "Any relevant caveats or context from the text",
        },
    },
    "required": ["confidence", "source_citation"],
}


class LiteratureExtractor:
    """Extract structured epidemiological parameters from scientific text.

    Uses LLM to parse PubMed abstracts, WHO guidelines, and technical
    assessment reports into a structured format compatible with the
    cost-effectiveness model.

    Args:
        client: An initialized LLMClient instance.

    Example:
        >>> client = LLMClient(provider="mimo")
        >>> extractor = LiteratureExtractor(client)
        >>> params = extractor.extract(pubmed_abstract)
        >>> print(params.vaccine_efficacy)  # 0.42
    """

    def __init__(self, client: LLMClient):
        self.client = client

    def extract(self, text: str, source_name: str = "") -> ExtractedParams:
        """Extract epidemiological parameters from a text passage.

        Args:
            text: Scientific text (PubMed abstract, guideline section, etc.)
            source_name: Optional identifier for the source document.

        Returns:
            ExtractedParams dataclass with extracted values.
        """
        extraction_task = (
            "Extract ALL numerical epidemiological and economic parameters "
            "from the following text. Include vaccine efficacy (VE), resistance "
            "rates, serial interval, R0, hospitalization rates, mortality rates, "
            "and drug costs. Report percentages as decimals (0.42 not 42%). "
            "For costs, use HKD if specified, otherwise use the original currency. "
            "Set confidence to 'high' if values come from primary data, "
            "'medium' for meta-analyses, 'low' for model assumptions."
        )

        if source_name:
            extraction_task += f"\nSource: {source_name}"

        try:
            raw = self.client.extract_from_text(
                text=text,
                extraction_task=extraction_task,
                output_schema=PARAMS_EXTRACTION_SCHEMA,
                temperature=0.1,  # Low temperature for factual extraction
            )

            # Merge with source_name if provided
            if source_name and raw.get("source_citation") == "":
                raw["source_citation"] = source_name

            return ExtractedParams(**{k: raw.get(k) for k in PARAMS_EXTRACTION_SCHEMA["properties"]})

        except Exception as e:
            logger.error("Extraction failed for source '%s': %s", source_name, e)
            return ExtractedParams(
                confidence="low",
                source_citation=source_name,
                notes=f"Extraction failed: {str(e)}",
            )

    def extract_batch(
        self, texts: list[tuple[str, str]]
    ) -> list[ExtractedParams]:
        """Extract parameters from multiple texts.

        Args:
            texts: List of (text, source_name) tuples.

        Returns:
            List of ExtractedParams, one per input text.
        """
        results = []
        for text, source_name in texts:
            logger.info("Extracting from: %s", source_name)
            params = self.extract(text, source_name)
            results.append(params)
        return results

    def merge_extractions(
        self, extractions: list[ExtractedParams], priority: str = "high_confidence"
    ) -> ExtractedParams:
        """Merge multiple extractions into a single consensus.

        When values conflict, uses the extraction with the highest confidence.
        For numeric values, can also compute weighted averages.

        Args:
            extractions: List of ExtractedParams to merge.
            priority: Merge strategy ("high_confidence" or "average").

        Returns:
            Merged ExtractedParams with consensus values.
        """
        confidence_order = {"high": 3, "medium": 2, "low": 1}

        # Sort by confidence (highest first)
        sorted_extractions = sorted(
            extractions, key=lambda x: confidence_order.get(x.confidence, 0), reverse=True
        )

        merged = ExtractedParams()
        sources = []

        for params in sorted_extractions:
            for field_name in [
                "vaccine_efficacy", "resistance_frequency", "serial_interval",
                "r0_low", "r0_mid", "r0_high", "symptomatic_proportion",
                "hospitalization_rate", "icu_rate", "case_fatality_rate",
                "cost_per_course_bxm_hkd", "cost_per_course_otv_hkd",
            ]:
                current_val = getattr(merged, field_name)
                new_val = getattr(params, field_name)

                if current_val is None and new_val is not None:
                    setattr(merged, field_name, new_val)

            if params.source_citation:
                sources.append(params.source_citation)

        merged.confidence = sorted_extractions[0].confidence if sorted_extractions else "low"
        merged.source_citation = "; ".join(sources) if sources else ""
        merged.notes = f"Merged from {len(extractions)} source(s)"

        return merged
