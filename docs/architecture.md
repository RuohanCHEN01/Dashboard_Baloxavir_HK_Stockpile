# System Architecture

## Overview

The Baloxavir Stockpile Dashboard follows a three-layer architecture:

1. **AI/Agent Layer** — LLM-powered analysis and automation
2. **Core Analytics Engine** — Epidemiological modeling and cost-effectiveness calculations
3. **Presentation Layer** — Interactive Streamlit dashboard

## Data Flow

```
[PubMed/WHO Guidelines] ──→ [AI Agent Layer] ──→ [Structured Parameters]
                                                         │
                                                         ▼
[HK Epidemiological Data] ──→ [Core Analytics] ──→ [Simulation Results]
                                                         │
                                                         ▼
                                                  [Presentation Layer]
                                                  [Streamlit Dashboard]
                                                         │
                                                    ┌────┴────┐
                                                    │ Export  │
                                                 [PDF] [CSV] [HTML]
```

## AI Agent Layer

The AI layer provides four core capabilities:

| Component | Input | Output | LLM Usage |
|-----------|-------|--------|-----------|
| Literature Extractor | PubMed abstracts | Structured parameters | Structured extraction |
| NL Query Engine | Natural language questions | Data-backed answers | RAG + synthesis |
| Report Generator | Analysis results | Policy brief markdown | Summarization |
| Parameter Optimizer | Search constraints | Optimal configs | ReAct reasoning |

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Streamlit, Plotly, Matplotlib |
| Backend | Python 3.11, pandas, numpy, scipy |
| AI/LLM | OpenAI SDK (compatible with MiMo, Claude, DeepSeek) |
| Modeling | R (via reticulate), custom SEIR/SMM models |
| Data | PostgreSQL/SQLite, CSV/Excel |
| CI/CD | GitHub Actions |
| Deployment | Streamlit Cloud (planned) |
