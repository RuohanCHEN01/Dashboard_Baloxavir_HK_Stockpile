"""
AI Agent Module for Baloxavir Stockpile Dashboard

This module provides LLM-powered capabilities for public health decision support:
- Literature evidence extraction from PubMed abstracts and WHO guidelines
- Intelligent parameter suggestion based on epidemiological evidence
- Automated policy brief generation in multiple languages
- Natural language interface for scenario queries

Supported LLM Providers:
    - OpenAI (GPT-4o, GPT-4-turbo)
    - Anthropic Claude (3.5 Sonnet, 3 Opus)
    - Xiaomi MiMo (V2.5-Pro, V2.5, V2-Flash)
    - DeepSeek (V3, R1)

Usage:
    >>> from ai_agent import LLMClient, LiteratureExtractor
    >>> client = LLMClient(provider="openai")
    >>> extractor = LiteratureExtractor(client)
    >>> params = extractor.extract("Influenza vaccine effectiveness was 42%...")
"""

__version__ = "2.0.0"
__author__ = "Ruohan Chen"

from .llm_interface import LLMClient
from .literature_extractor import LiteratureExtractor
from .report_generator import PolicyReportGenerator
from .nl_query import NLQueryEngine

__all__ = [
    "LLMClient",
    "LiteratureExtractor",
    "PolicyReportGenerator",
    "NLQueryEngine",
]
