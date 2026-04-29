"""AI Agent module configuration."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"

# Default LLM settings
DEFAULT_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
DEFAULT_MODEL = os.environ.get("LLM_MODEL", "")
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 4096

# Extraction settings
EXTRACTION_CONFIDENCE_THRESHOLD = 0.7
MAX_EXTRACTION_RETRIES = 3

# Report generation settings
REPORT_LANGUAGE = os.environ.get("REPORT_LANGUAGE", "en")
REPORT_OUTPUT_DIR = Path("output/reports")

# Logging
LOG_LEVEL = os.environ.get("AI_AGENT_LOG_LEVEL", "INFO")
