"""
Configuration module for Secure LLM Code Generator.

This module loads environment variables from a .env file
and makes them available throughout the project.
"""

import os
from dotenv import load_dotenv

# --------------------------------------------------
# Load variables from the .env file
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Read configuration values
# --------------------------------------------------

# Gemini API Key
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# Gemini model name
GEMINI_MODEL: str = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.0-flash"
)

# Maximum generate → scan → fix iterations
MAX_ITERATIONS: int = int(
    os.getenv("MAX_ITERATIONS", "3")
)

# --------------------------------------------------
# Warn the user if API key is missing
# --------------------------------------------------
if not GEMINI_API_KEY:
    print(
        "[WARNING] GEMINI_API_KEY is missing. "
        "Please add it to your .env file."
    )