import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from tracing import tracing


class FakeModel:
    def invoke(self, prompt, config=None):
        assert config["metadata"]["request_id"] == "test-123"

        return AIMessage(
            content="LangSmith provides tracing and observability."
        )


class FailingModel:
    def invoke(self, prompt, config=None):
        assert config["metadata"]["request_id"] == "test-123"

        raise RuntimeError("Model unavailable")


def fake_retriever(query, **kwargs):
    request_id = kwargs["langsmith_extra"]["metadata"]["request_id"]

    assert request_id == "test-123"

    return [
        Document(
            page_content=("LangSmith provides tracing and observability.")
        )
    ]


def test_tracing_success(monkeypatch):

    monkeypatch.setattr( tracing,"model", FakeModel())

    monkeypatch.setattr(tracing,"retrieve_documents", fake_retriever,)

    result = tracing.run_request("What does LangSmith provide?","test-123")

    assert result == ("LangSmith provides tracing and observability.")


def test_tracing_failure(monkeypatch):

    monkeypatch.setattr(tracing,"model",FailingModel())

    monkeypatch.setattr(tracing, "retrieve_documents", fake_retriever)

    with pytest.raises( RuntimeError, match="Model unavailable"):
        tracing.run_request("What does LangSmith provide?","test-123")