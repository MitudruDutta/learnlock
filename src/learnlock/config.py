"""Configuration for learn-lock. All configurable values in one place."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load local configuration without overriding already-exported shell variables.
load_dotenv(Path.cwd() / ".env", override=False)
load_dotenv(Path.home() / ".learnlock" / ".env", override=False)


def _int(env_var: str, default: int) -> int:
    """Parse an integer from an environment variable, returning default on failure."""
    raw = os.getenv(env_var)
    if raw is None:
        return default
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def _float(env_var: str, default: float) -> float:
    """Parse a float from an environment variable, returning default on failure."""
    raw = os.getenv(env_var)
    if raw is None:
        return default
    try:
        return float(raw)
    except (ValueError, TypeError):
        return default


# ============ PATHS ============
DATA_DIR = Path(os.getenv("LEARNLOCK_DATA_DIR", Path.home() / ".learnlock"))
DB_PATH = DATA_DIR / "data.db"

# ============ LLM MODELS ============
GROQ_MODEL = os.getenv("LEARNLOCK_GROQ_MODEL", "openai/gpt-oss-120b")
GEMINI_MODEL = os.getenv("LEARNLOCK_GEMINI_MODEL", "gemini-2.5-flash")

# ============ LLM PARAMETERS ============
LLM_MAX_TOKENS = _int("LEARNLOCK_LLM_MAX_TOKENS", 2000)
LLM_TEMPERATURE = _float("LEARNLOCK_LLM_TEMPERATURE", 0.3)
CONTENT_MAX_CHARS = _int("LEARNLOCK_CONTENT_MAX_CHARS", 8000)
CONTENT_TRUNCATE_FOR_PROMPT = _int("LEARNLOCK_CONTENT_TRUNCATE_FOR_PROMPT", 6000)
MAX_STORED_CONTENT_CHARS = _int("LEARNLOCK_MAX_STORED_CONTENT_CHARS", 250000)

# ============ NETWORK / STORAGE SAFETY ============
MAX_REMOTE_DOWNLOAD_BYTES = _int("LEARNLOCK_MAX_REMOTE_DOWNLOAD_BYTES", 20971520)
SQLITE_TIMEOUT_SECONDS = _float("LEARNLOCK_SQLITE_TIMEOUT_SECONDS", 10)
MAX_YOUTUBE_DURATION_SECONDS = _int("LEARNLOCK_MAX_YOUTUBE_DURATION_SECONDS", 7200)
AUTO_EXPORT_DUELS = os.getenv("LEARNLOCK_AUTO_EXPORT_DUELS", "0").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# ============ SPACED REPETITION (SM-2) ============
SM2_INITIAL_EASE = _float("LEARNLOCK_SM2_INITIAL_EASE", 2.5)
SM2_INITIAL_INTERVAL = _float("LEARNLOCK_SM2_INITIAL_INTERVAL", 1.0)
SM2_MIN_EASE = _float("LEARNLOCK_SM2_MIN_EASE", 1.3)
SM2_MAX_INTERVAL = _float("LEARNLOCK_SM2_MAX_INTERVAL", 180)

# ============ MASTERY THRESHOLDS ============
MASTERY_MIN_EASE = _float("LEARNLOCK_MASTERY_MIN_EASE", 2.5)
MASTERY_MIN_REVIEWS = _int("LEARNLOCK_MASTERY_MIN_REVIEWS", 3)

# ============ GRADING ============
SCORE_MIN = _int("LEARNLOCK_SCORE_MIN", 1)
SCORE_MAX = _int("LEARNLOCK_SCORE_MAX", 5)
SCORE_PASS_THRESHOLD = _int("LEARNLOCK_SCORE_PASS_THRESHOLD", 3)
DEFAULT_FALLBACK_SCORE = _int("LEARNLOCK_DEFAULT_FALLBACK_SCORE", 3)

# ============ EXTRACTION ============
MIN_CONCEPTS = _int("LEARNLOCK_MIN_CONCEPTS", 8)
MAX_CONCEPTS = _int("LEARNLOCK_MAX_CONCEPTS", 12)
EXTRACTION_MAX_RETRIES = _int("LEARNLOCK_EXTRACTION_MAX_RETRIES", 2)

# ============ TEXT LIMITS ============
MAX_CONCEPT_NAME_LENGTH = _int("LEARNLOCK_MAX_CONCEPT_NAME_LENGTH", 200)
MAX_QUOTE_LENGTH = _int("LEARNLOCK_MAX_QUOTE_LENGTH", 500)
MAX_EXPLANATION_LENGTH = _int("LEARNLOCK_MAX_EXPLANATION_LENGTH", 2000)
MAX_FEEDBACK_LENGTH = _int("LEARNLOCK_MAX_FEEDBACK_LENGTH", 500)
MAX_COVERED_MISSED_ITEMS = _int("LEARNLOCK_MAX_COVERED_MISSED_ITEMS", 5)
MAX_COVERED_MISSED_LENGTH = _int("LEARNLOCK_MAX_COVERED_MISSED_LENGTH", 200)

# ============ OCR ============
MAX_IMAGE_FILE_BYTES = _int("LEARNLOCK_MAX_IMAGE_FILE_BYTES", 10 * 1024 * 1024)  # 10MB

# ============ RATE LIMITING ============
LLM_MIN_CALL_INTERVAL = _float("LEARNLOCK_LLM_MIN_CALL_INTERVAL", 0.2)
LLM_MAX_RETRIES = _int("LEARNLOCK_LLM_MAX_RETRIES", 2)
LLM_BACKOFF_BASE = _float("LEARNLOCK_LLM_BACKOFF_BASE", 1.0)
