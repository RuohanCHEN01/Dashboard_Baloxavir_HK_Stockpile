# User Guide

## Getting Started

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
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
LLM_PROVIDER=mimo
MIMO_API_KEY=your_api_key_here
```

### Running the Dashboard

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Features

### Core Dashboard
- **Scenario Analysis**: Compare different antiviral stockpile strategies
- **Cost-Effectiveness**: View ICER, NMB, and CEAC results
- **Interactive Charts**: Hover, zoom, and filter data visualizations
- **Data Export**: Download results as CSV or PDF

### AI-Powered Features
- **Literature Extraction**: Extract parameters from PubMed abstracts
- **Smart Search**: Query results using natural language
- **Report Generation**: Generate policy briefs automatically

See [AI Module Guide](ai_module_guide.md) for detailed AI feature documentation.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Ensure venv is activated and deps installed |
| API key error | Check `.env` file has correct keys |
| Dashboard won't load | Run `streamlit run app.py` from project root |
| Data not found | Ensure CSV/Excel data files are in the `data/` directory |
