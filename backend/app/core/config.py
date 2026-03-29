import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend/ directory (where this project runs from)
_backend_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(_backend_dir / ".env")
# Also try project root .env as fallback
load_dotenv(_backend_dir.parent / ".env")

logger = logging.getLogger(__name__)


def get_env(key: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if required and not value:
        logger.critical(f"Missing required environment variable: {key}")
        sys.exit(1)
    if not required and not value:
        logger.warning(f"Optional environment variable not set: {key}")
    return value


GOOGLE_API_KEY: str = get_env("GOOGLE_API_KEY")  # type: ignore
ELEVENLABS_API_KEY: str = get_env("ELEVENLABS_API_KEY")  # type: ignore
GOOGLE_CLOUD_PROJECT: str | None = get_env("GOOGLE_CLOUD_PROJECT", required=False)

CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
APP_ENV: str = os.getenv("APP_ENV", "development")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))

ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
