import sys
import re
from loguru import logger
from backend.app.core.config import settings

# Sensitive keys to redact
SENSITIVE_PATTERNS = [
    re.compile(r'("?(?:password|token|secret|access_token|authorization)"?\s*[:=]\s*"?)([^",\s]+)("?)', re.IGNORECASE),
    re.compile(r'(Bearer\s+)([A-Za-z0-9\-\._~\+\/]+=*)', re.IGNORECASE)
]


def redact_sensitive_data(message: str) -> str:
    redacted = message
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(r'\1[REDACTED]\3', redacted)
    return redacted


def setup_logging():
    logger.remove()

    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )

    # Use sys.stderr with utf-8 reconfigure or safe text format
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=log_format,
        colorize=False
    )

    # File logger for audit & observability
    logger.add(
        "logs/medassist_{time:YYYY-MM-DD}.log",
        rotation="50 MB",
        retention="30 days",
        level="INFO",
        encoding="utf-8"
    )

    return logger


app_logger = setup_logging()
