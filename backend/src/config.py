"""
Configuration module for AISAF.

Loads environment variables from the .env file.
"""

import os
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

# --------------------------------------------------
# Gemini Configuration
# --------------------------------------------------

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL: str = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

# --------------------------------------------------
# Pipeline Configuration
# --------------------------------------------------

MAX_ITERATIONS: int = int(
    os.getenv("MAX_ITERATIONS", "3")
)

OUTPUT_DIR: str = os.getenv(
    "OUTPUT_DIR",
    "output"
)

# --------------------------------------------------
# Validate Configuration
# --------------------------------------------------

if not GEMINI_API_KEY:
    print(
        "[WARNING] GEMINI_API_KEY is missing. "
        "Please add it to your .env file."
    )