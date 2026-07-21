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

# Groq API Key
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# Groq model name
GROQ_MODEL: str = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

# Maximum generate → scan → fix iterations
MAX_ITERATIONS: int = int(
    os.getenv("MAX_ITERATIONS", "3")
)

# --------------------------------------------------
# Warn the user if API key is missing
# --------------------------------------------------
if not GROQ_API_KEY:
    print(
        "[WARNING] GROQ_API_KEY is missing. "
        "Please add it to your .env file."
    )
