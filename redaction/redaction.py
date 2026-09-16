import json
import logging
import re

logging.basicConfig(level=logging.INFO,format="%(message)s")

logger = logging.getLogger("redaction")

EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

API_KEY_PATTERN = re.compile( r"\bsk-[A-Za-z0-9_-]{8,}\b")


def redact(text: str) -> str:
    """Remove sensitive information before logging."""

    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]",text)

    text = API_KEY_PATTERN.sub("[REDACTED_API_KEY]",text)

    return text


def safe_log(message: str):
    """Redact sensitive information and write a JSON log."""

    safe_message = redact(message)

    log_data = {
        "message": safe_message
    }

    logger.info(
        json.dumps(log_data)
    )


if __name__ == "__main__":

    safe_log(
        "Contact ada@example.com "
        "using key sk-abcdefgh12345"
    )