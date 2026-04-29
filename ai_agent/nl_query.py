"""
Natural Language Query Engine.

Allows users to query scenario analysis results using natural language
(e.g., "What is the ICER when BXM covers 30% of the population?").
Uses RAG-style retrieval over simulation results + LLM for answer synthesis.
"""

import json
import logging
from typing import Optional

from .llm_interface import LLMClient

logger = logging.getLogger(__name__)


class NLQueryEngine:
    """Natural language query interface for scenario analysis results.

    Users can ask questions about simulation outcomes in plain English/Chinese
    and receive structured answers with data citations.

    Args:
        client: An initialized LLMClient instance.

    Example:
        >>> client = LLMClient(provider="mimo")
        >>> engine = NLQueryEngine(client)
        >>> engine.load_results(scenario_results)
        >>> answer = engine.query(
        ...     "What is the ICER when BXM stockpile covers 30% of population?"
        ... )
    """

    def __init__(self, client: LLMClient):
        self.client = client
        self._results_cache: list[dict] = []
        self._results_summary: str = ""

    def load_results(self, results: list[dict]) -> None:
        """Load scenario analysis results for querying.

        Args:
            results: List of scenario result dictionaries. Each should contain
                     at minimum: scenario_name, icer, total_cost, qaly,
                     and any relevant parameters.
        """
        self._results_cache = results
        self._results_summary = json.dumps(
            results, indent=2, ensure_ascii=False, default=str
        )
        logger.info("Loaded %d scenario results for NL querying", len(results))

    def query(self, question: str, language: str = "en") -> dict:
        """Ask a natural language question about the loaded results.

        Args:
            question: Natural language question about the analysis.
            language: Response language ("en" or "zh").

        Returns:
            Dictionary with 'answer', 'data_references', and 'confidence'.
        """
        if not self._results_cache:
            return {
                "answer": "No scenario results loaded. Call load_results() first.",
                "data_references": [],
                "confidence": "none",
            }

        lang_instruction = (
            "Respond in English." if language == "en"
            else "请用中文回答。"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert health economics analyst. Answer questions "
                    "about cost-effectiveness analysis results accurately and concisely. "
                    f"{lang_instruction} "
                    "Always cite specific data values from the results. "
                    "If the exact answer is not available in the data, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Available scenario analysis data:\n{self._results_summary}"
                ),
            },
        ]

        try:
            answer = self.client.complete(
                messages=messages,
                temperature=0.2,
                max_tokens=1024,
            )

            return {
                "answer": answer,
                "data_references": self._find_relevant_scenarios(question),
                "confidence": "high",
                "question": question,
            }

        except Exception as e:
            logger.error("NL query failed: %s", e)
            return {
                "answer": f"Query processing error: {e}",
                "data_references": [],
                "confidence": "error",
                "question": question,
            }

    def _find_relevant_scenarios(self, question: str) -> list[str]:
        """Simple keyword matching to find relevant scenarios.

        Args:
            question: User question text.

        Returns:
            List of scenario names that may be relevant.
        """
        question_lower = question.lower()
        relevant = []

        for result in self._results_cache:
            scenario_name = result.get("scenario_name", "")
            result_str = json.dumps(result, default=str).lower()

            # Check if any keyword from the question appears in the result
            keywords = [
                w for w in question_lower.split()
                if len(w) > 3 and w not in ("what", "when", "which", "that", "this", "with")
            ]

            matches = sum(1 for kw in keywords if kw in result_str)
            if matches >= 2:
                relevant.append(scenario_name)

        return relevant[:5]  # Return top 5 matches
