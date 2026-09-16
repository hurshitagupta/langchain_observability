import pytest
from langchain_core.messages import AIMessage

from metrics_and_dashboard import metrics_and_dashboard


class FakeSuccessModel:
    def invoke(self, question):
        return AIMessage(content="Observability helps monitor applications.")


class FakeFailureModel:
    def invoke(self, question):
        raise RuntimeError("Model unavailable")


def get_counter_value(counter):
    return counter._value.get()


def get_histogram_count(histogram):
    for metric in histogram.collect():
        for sample in metric.samples:
            if sample.name.endswith("_count"):
                return sample.value

    return 0


def test_metrics_success(monkeypatch):

    monkeypatch.setattr( metrics_and_dashboard,"model", FakeSuccessModel())

    requests_before = get_counter_value(metrics_and_dashboard.REQUEST_COUNT)

    errors_before = get_counter_value(metrics_and_dashboard.ERROR_COUNT)

    latency_before = get_histogram_count(
        metrics_and_dashboard.LATENCY
    )

    result = metrics_and_dashboard.observed_model_call("What is observability?")

    requests_after = get_counter_value(metrics_and_dashboard.REQUEST_COUNT)

    errors_after = get_counter_value( metrics_and_dashboard.ERROR_COUNT)

    latency_after = get_histogram_count(metrics_and_dashboard.LATENCY)

    assert result == ("Observability helps monitor applications.")

    assert requests_after == requests_before + 1
    assert errors_after == errors_before
    assert latency_after == latency_before + 1


def test_metrics_failure(monkeypatch):

    monkeypatch.setattr( metrics_and_dashboard, "model", FakeFailureModel())

    requests_before = get_counter_value(metrics_and_dashboard.REQUEST_COUNT)

    errors_before = get_counter_value(metrics_and_dashboard.ERROR_COUNT)

    latency_before = get_histogram_count(metrics_and_dashboard.LATENCY)

    with pytest.raises(RuntimeError,match="Model unavailable"):
        metrics_and_dashboard.observed_model_call("What is observability?")

    requests_after = get_counter_value(metrics_and_dashboard.REQUEST_COUNT)

    errors_after = get_counter_value(metrics_and_dashboard.ERROR_COUNT)

    latency_after = get_histogram_count(metrics_and_dashboard.LATENCY)

    assert requests_after == requests_before + 1
    assert errors_after == errors_before + 1
    assert latency_after == latency_before + 1