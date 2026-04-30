# AI Module Guide

## Overview

The `ai_agent/` module provides LLM-powered capabilities for enhancing public health decision support. It integrates with multiple LLM providers through a unified interface.

## Architecture

```
ai_agent/
├── __init__.py              # Module exports
├── llm_interface.py         # Multi-provider LLM client
├── literature_extractor.py  # PubMed evidence extraction
├── report_generator.py      # AI policy brief generation
├── nl_query.py             # Natural language query engine
├── config.py               # Configuration
└── prompts/                # YAML prompt templates
    ├── system_prompts.yaml
    └── extraction_prompts.yaml
```

## Quick Start

### Initialize LLM Client

```python
from ai_agent import LLMClient

# Use MiMo (1M context window)
client = LLMClient(provider="mimo", model="mimo-v2.5-pro")

# Use OpenAI
client = LLMClient(provider="openai", model="gpt-4o")

# Use DeepSeek (cost-effective)
client = LLMClient(provider="deepseek")
```

### Extract Parameters from Literature

```python
from ai_agent import LiteratureExtractor

extractor = LiteratureExtractor(client)

abstract = """
Background: Influenza vaccine effectiveness (VE) against influenza A(H3N2)
was estimated at 42% (95% CI: 31-52%) during the 2024-25 season.
Oseltamivir resistance was detected in 3.5% of tested isolates.
"""

params = extractor.extract(abstract, source_name="PubMed Abstract 2025")
print(params.vaccine_efficacy)  # 0.42
print(params.resistance_frequency)  # 0.035
print(params.confidence)  # "high"
```

### Query Results in Natural Language

```python
from ai_agent import NLQueryEngine

engine = NLQueryEngine(client)
engine.load_results([
    {"scenario_name": "BXM_30pct", "icer": 15000, "nmb": 2500000},
    {"scenario_name": "OTV_30pct", "icer": 22000, "nmb": -500000},
])

answer = engine.query("Which strategy is more cost-effective at 30% coverage?")
print(answer["answer"])
```

### Generate Policy Brief

```python
from ai_agent import PolicyReportGenerator

gen = PolicyReportGenerator(client)
report = gen.generate_full_report(
    analysis_data={"icer": 15000, "qaly": 0.05},
    title="BXM Stockpile Strategy 2026",
)
gen.save_markdown(report, "output/policy_brief.md")
```

## Supported Providers

| Provider | Setup | Best For |
|----------|-------|----------|
| MiMo | `MIMO_API_KEY` env var | Long documents (1M context) |
| OpenAI | `OPENAI_API_KEY` env var | General purpose |
| Claude | `ANTHROPIC_API_KEY` env var | Complex reasoning |
| DeepSeek | `DEEPSEEK_API_KEY` env var | Cost-effective analysis |
