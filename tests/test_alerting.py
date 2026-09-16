import logging

from alerting import alerting


def test_latency_healthy(caplog):

    with caplog.at_level(logging.INFO,logger="alerting"):
        alert_fired = alerting.check_latency(1.0)

    assert alert_fired is False

    assert "Latency healthy" in caplog.text
    assert "ALERT" not in caplog.text


def test_latency_alert(caplog):

    with caplog.at_level(logging.WARNING,logger="alerting"):
        alert_fired = alerting.check_latency(3.0)

    assert alert_fired is True

    assert ("ALERT: latency regression detected" in caplog.text)