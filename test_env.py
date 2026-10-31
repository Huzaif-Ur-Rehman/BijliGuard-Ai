"""Verify virtual-environment activation and local Gemini configuration."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

environment_active = sys.prefix != sys.base_prefix
api_key = os.getenv("GEMINI_API_KEY", "").strip()
api_key_configured = api_key not in {"", "your_gemini_api_key_here"}
model_configured = bool(os.getenv("DEFAULT_VISION_MODEL", "").strip())

print(f"Virtual environment active: {'yes' if environment_active else 'no'}")
print(f"Gemini API key loaded: {'yes' if api_key_configured else 'no'}")
print(f"Vision model configured: {'yes' if model_configured else 'no'}")

if not environment_active or not api_key_configured or not model_configured:
    raise SystemExit(1)

print("Environment checks passed. The API key was not displayed.")
