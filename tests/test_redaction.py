import json
import logging

from redaction import redaction


def test_redaction_success(caplog):

    sensitive_message = (
        "Contact ada@example.com "
        "using key sk-abcdefgh12345"
    )

    with caplog.at_level(logging.INFO, logger="redaction"):
        redaction.safe_log(sensitive_message)

    log_data = json.loads( caplog.records[-1].message)

    logged_message = log_data["message"]

    assert "ada@example.com" not in logged_message
    assert "sk-abcdefgh12345" not in logged_message

    assert "[REDACTED_EMAIL]" in logged_message
    assert "[REDACTED_API_KEY]" in logged_message


def test_redaction_failure_detection():

    unsafe_log = (
        "User email is ada@example.com "
        "and key is sk-abcdefgh12345"
    )

    email_found = redaction.EMAIL_PATTERN.search(unsafe_log)

    api_key_found = redaction.API_KEY_PATTERN.search(unsafe_log)
    assert email_found is not None
    assert api_key_found is not None