# User Guide

## Online Demo

The dashboard is publicly available at:

**https://dashboardbaloxavirhkstockpile-7r4ydhrwws9erayhwprou6.streamlit.app/**

No installation required — just open the link in your browser.

## Getting Started (Local Installation)

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- An LLM API key (for AI features)

### Installation

```bash
# Clone and navigate to the project
git clone https://github.com/RuohanCHEN01/Dashboard_Baloxavir_HK_Stockpile.git
cd Dashboard_Baloxavir_HK_Stockpile

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venvScriptsactivate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your preferred LLM provider and API key:

```env
LLM_PROVIDER=mimo
MIMO_API_KEY=your_mimo_api_key
```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

## Dashboard Overview

### Navigation

The sidebar provides the following navigation options:

| Page | Description |
|------|-------------|
| **Overview** | KPI summary, AI feature showcase, LLM provider table |
| **Scenario Analysis** | 66 BXM/OTV/ZNV combinations with scatter plot, AR/RAR heatmaps, and top-10 table |
| **Cost-Effectiveness** | CE plane, cost breakdown, WTP threshold analysis |
| **Hospitalization** | 500-day time series with multi-scenario comparison |
| **AI Agent Demo** | 4 tabs: Provider Overview, Literature Extraction, NL Query, Policy Report |

### Filters

Use the sidebar sliders to filter scenarios by BXM and OTV proportion ranges.

## Using AI Features

### Literature Extraction

1. Navigate to the **AI Agent Demo** page
2. Select the **Literature Extraction** tab
3. View sample extraction from a PubMed abstract

The extraction agent automatically identifies key epidemiological parameters
(vaccine efficacy, resistance rates, serial interval, etc.) using LLM reasoning.

### Natural Language Query

The NL Query engine can answer questions about the simulation results.

Example queries:
- "What is the ICER when BXM covers 30% of the population?"
- "Which strategy minimizes hospitalizations?"
- "Compare BXM-only vs OTV-only cost-effectiveness"

### Policy Report Generation

Generate structured policy briefs with AI-summarized findings:

1. Choose **Policy Report** tab in AI Agent Demo
2. Select report section (Executive Summary, Key Findings, etc.)
3. Review and export the generated report

## Data Export

- CSV export available for scenario data tables
- Interactive charts can be downloaded as PNG/SVG
- Policy reports can be saved as Markdown files

## Getting Help

For issues or questions:
- Open a GitHub issue: https://github.com/RuohanCHEN01/Dashboard_Baloxavir_HK_Stockpile/issues
- Contact: ruohan0@connect.hku.hk

