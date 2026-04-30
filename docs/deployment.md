# Streamlit Cloud Deployment Guide

## 🔗 Live Deployment

The dashboard is deployed at:

**https://dashboardbaloxavirhkstockpile-7r4ydhrwws9erayhwprou6.streamlit.app/**

## Deploy to Streamlit Community Cloud

### Prerequisites

1. A [GitHub](https://github.com) account
2. The project repository pushed to GitHub
3. A [Streamlit Community Cloud](https://streamlit.io/cloud) account (free)

### Steps

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select the repository: `RuohanCHEN01/Dashboard_Baloxavir_HK_Stockpile`
4. Select the branch: `main`
5. Set the main file path: `app.py`
6. Click "Deploy"

### Environment Variables (Optional)

For AI features, add these secrets in the Streamlit Cloud settings:

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | Your preferred LLM provider (e.g., `mimo`) |
| `MIMO_API_KEY` | Xiaomi MiMo API key |
| `OPENAI_API_KEY` | OpenAI API key (alternative) |

To add secrets: App > Settings > Secrets > Edit

### Troubleshooting

- If the app fails to load, check the logs in the Streamlit Cloud dashboard
- Ensure `requirements.txt` includes all dependencies
- The `.streamlit/config.toml` is pre-configured for cloud deployment

## Deploy to Hugging Face Spaces (Alternative)

```bash
# Create a Dockerfile-based Space
# Dockerfile content:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
