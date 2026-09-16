import json
import logging

import pytest
from langchain_core.messages import AIMessage

from structured_logging import structured_logging


class FakeSuccessModel:
    def invoke(self, question):
        return AIMessage(
            content="Observability helps monitor an application.",
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
        )


class FakeFailureModel:
    def invoke(self, question):
        raise RuntimeError("Model unavailable")


def test_successful_structured_log(monkeypatch, caplog):

    monkeypatch.setattr(structured_logging,"model",FakeSuccessModel())

    with caplog.at_level(logging.INFO,logger="observability"):
        result = structured_logging.observed_invoke("What is observability?")

    log_data = json.loads(caplog.records[-1].message)

    assert result == "Observability helps monitor an application."

    assert log_data["request_id"]
    assert log_data["step"] == "model_call"
    assert log_data["duration_ms"] >= 0
    assert log_data["tokens"] == 15
    assert log_data["outcome"] == "success"


def test_failed_structured_log(monkeypatch, caplog):

    monkeypatch.setattr(structured_logging,"model",FakeFailureModel())

    with caplog.at_level(logging.INFO,logger="observability"):
        with pytest.raises(RuntimeError):
            structured_logging.observed_invoke("What is observability?")

    log_data = json.loads(caplog.records[-1].message)

    assert log_data["request_id"]
    assert log_data["step"] == "model_call"
    assert log_data["duration_ms"] >= 0
    assert log_data["tokens"] == 0
    assert log_data["outcome"] == "failure"