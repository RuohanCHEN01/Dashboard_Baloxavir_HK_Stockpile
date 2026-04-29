"""
AI-Powered Policy Report Generator.

Generates professional PDF policy briefs with LLM-summarized key findings,
sensitivity analysis highlights, and actionable recommendations for health
authorities.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from .llm_interface import LLMClient

logger = logging.getLogger(__name__)


# Report section prompts
SECTION_PROMPTS = {
    "executive_summary": (
        "Write a concise executive summary (200-300 words) for health policy makers. "
        "Focus on: 1) Key decision point, 2) Main findings in plain language, "
        "3) Recommended action. Use bullet points where appropriate."
    ),
    "key_findings": (
        "Summarize the key quantitative findings from the analysis. "
        "Include specific ICER values, cost savings, health outcomes, "
        "and confidence intervals. Present as a structured list."
    ),
    "sensitivity_analysis": (
        "Describe the sensitivity analysis results. Which parameters "
        "most significantly affect the cost-effectiveness conclusion? "
        "What are the threshold values at which the optimal strategy changes?"
    ),
    "policy_recommendations": (
        "Based on the analysis results, provide 3-5 specific, actionable "
        "policy recommendations for the health authority. Consider: "
        "stockpile size, drug mix, trigger thresholds, and monitoring needs."
    ),
    "limitations": (
        "List the key limitations and assumptions of the analysis. "
        "Be specific about data sources, model structure, and generalizability."
    ),
}


class PolicyReportGenerator:
    """Generate AI-enhanced policy briefs from analysis results.

    Takes structured analysis data and generates professional policy brief
    sections using LLM summarization and formatting capabilities.

    Args:
        client: An initialized LLMClient instance.

    Example:
        >>> client = LLMClient(provider="mimo")
        >>> gen = PolicyReportGenerator(client)
        >>> report = gen.generate(analysis_data, title="HK BXM Stockpile Strategy 2026")
        >>> report.save_pdf("output/policy_brief.pdf")
    """

    def __init__(self, client: LLMClient):
        self.client = client

    def generate_section(
        self,
        section_name: str,
        analysis_data: dict,
        context: str = "",
    ) -> str:
        """Generate a single report section using LLM.

        Args:
            section_name: Name of the section (key in SECTION_PROMPTS).
            analysis_data: Dictionary of analysis results.
            context: Additional context or instructions.

        Returns:
            Generated section text in markdown format.
        """
        if section_name not in SECTION_PROMPTS:
            raise ValueError(
                f"Unknown section '{section_name}'. "
                f"Available: {list(SECTION_PROMPTS.keys())}"
            )

        prompt = SECTION_PROMPTS[section_name]
        data_str = json.dumps(analysis_data, indent=2, ensure_ascii=False, default=str)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior health economics advisor writing policy briefs "
                    "for the Hong Kong Centre for Health Protection (CHP). Write in "
                    "a clear, professional tone suitable for senior government officials. "
                    "Use precise language and avoid unnecessary jargon."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{prompt}\n\n"
                    f"Analysis data:\n{data_str}\n\n"
                    f"{context}"
                ),
            },
        ]

        try:
            return self.client.complete(
                messages=messages,
                temperature=0.4,
                max_tokens=2048,
            )
        except Exception as e:
            logger.error("Section generation failed for '%s': %s", section_name, e)
            return f"[Error generating section: {e}]"

    def generate_full_report(
        self,
        analysis_data: dict,
        title: str = "Antiviral Stockpile Strategy: Cost-Effectiveness Analysis",
        subtitle: str = "",
        author: str = "HKU WHO CC Modelling Team",
        language: str = "en",
    ) -> dict:
        """Generate all sections of a complete policy brief.

        Args:
            analysis_data: Dictionary containing all analysis results.
            title: Report title.
            subtitle: Report subtitle.
            author: Author attribution.
            language: Output language ("en" or "zh").

        Returns:
            Dictionary with all generated sections and metadata.
        """
        report = {
            "metadata": {
                "title": title,
                "subtitle": subtitle,
                "author": author,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "language": language,
                "generated_by": "ai_agent.PolicyReportGenerator",
            },
            "sections": {},
        }

        # Generate each section
        for section_name in SECTION_PROMPTS:
            logger.info("Generating section: %s", section_name)
            report["sections"][section_name] = self.generate_section(
                section_name, analysis_data
            )

        return report

    def to_markdown(self, report: dict) -> str:
        """Convert report to markdown format.

        Args:
            report: Generated report dictionary.

        Returns:
            Complete markdown string.
        """
        meta = report["metadata"]
        lines = [
            f"# {meta['title']}",
            f"**{meta.get('subtitle', '')}**",
            "",
            f"*{meta['author']} | {meta['date']}*",
            "",
            "---",
            "",
        ]

        section_titles = {
            "executive_summary": "Executive Summary",
            "key_findings": "Key Findings",
            "sensitivity_analysis": "Sensitivity Analysis",
            "policy_recommendations": "Policy Recommendations",
            "limitations": "Limitations",
        }

        for section_key, content in report["sections"].items():
            title = section_titles.get(section_key, section_key.replace("_", " ").title())
            lines.extend([f"## {title}", "", content, ""])

        return "\n".join(lines)

    def save_markdown(self, report: dict, filepath: str) -> None:
        """Save report as markdown file.

        Args:
            report: Generated report dictionary.
            filepath: Output file path.
        """
        md_content = self.to_markdown(report)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info("Report saved to: %s", filepath)
