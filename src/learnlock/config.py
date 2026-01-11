"""Configuration for learn-lock. All configurable values in one place."""

import os
from pathlib import Path

# ============ PATHS ============
DATA_DIR = Path(os.getenv("LEARNLOCK_DATA_DIR", Path.home() / ".learnlock"))
DB_PATH = DATA_DIR / "data.db"

# ============ LLM MODELS ============
GROQ_MODEL = os.getenv("LEARNLOCK_GROQ_MODEL", "openai/gpt-oss-120b")
GEMINI_MODEL = os.getenv("LEARNLOCK_GEMINI_MODEL", "gemini-2.5-flash")

# ============ LLM PARAMETERS ============
LLM_MAX_TOKENS = int(os.getenv("LEARNLOCK_LLM_MAX_TOKENS", "2000"))
LLM_TEMPERATURE = float(os.getenv("LEARNLOCK_LLM_TEMPERATURE", "0.3"))
CONTENT_MAX_CHARS = int(os.getenv("LEARNLOCK_CONTENT_MAX_CHARS", "8000"))

# ============ SPACED REPETITION (SM-2) ============
SM2_INITIAL_EASE = float(os.getenv("LEARNLOCK_SM2_INITIAL_EASE", "2.5"))
SM2_INITIAL_INTERVAL = float(os.getenv("LEARNLOCK_SM2_INITIAL_INTERVAL", "1.0"))
SM2_MIN_EASE = float(os.getenv("LEARNLOCK_SM2_MIN_EASE", "1.3"))
SM2_MAX_INTERVAL = float(os.getenv("LEARNLOCK_SM2_MAX_INTERVAL", "180"))

# ============ MASTERY THRESHOLDS ============
MASTERY_MIN_EASE = float(os.getenv("LEARNLOCK_MASTERY_MIN_EASE", "2.5"))
MASTERY_MIN_REVIEWS = int(os.getenv("LEARNLOCK_MASTERY_MIN_REVIEWS", "3"))

# ============ GRADING ============
SCORE_MIN = 1
SCORE_MAX = 5
SCORE_PASS_THRESHOLD = 3  # Score >= this is considered pass
DEFAULT_FALLBACK_SCORE = 3  # Used when evaluation fails

# ============ EXTRACTION ============
MIN_CONCEPTS = int(os.getenv("LEARNLOCK_MIN_CONCEPTS", "3"))
MAX_CONCEPTS = int(os.getenv("LEARNLOCK_MAX_CONCEPTS", "5"))
