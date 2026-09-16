import logging
import time


logging.basicConfig(level=logging.INFO,format="%(message)s")

logger = logging.getLogger("alerting")

LATENCY_THRESHOLD = 2.0


def check_latency(duration: float) -> bool:
    """Check whether latency crossed the threshold."""

    if duration > LATENCY_THRESHOLD:

        logger.warning(
            f"ALERT: latency regression detected | "
            f"latency={duration:.2f}s | "
            f"threshold={LATENCY_THRESHOLD:.2f}s"
        )

        return True

    logger.info(
        f"Latency healthy | "
        f"latency={duration:.2f}s | "
        f"threshold={LATENCY_THRESHOLD:.2f}s"
    )

    return False


def normal_request():
    """Simulate a healthy request."""

    start = time.perf_counter()

    time.sleep(0.5)

    duration = time.perf_counter() - start

    check_latency(duration)


def broken_request():
    """Intentionally slow request to trigger the alert."""

    start = time.perf_counter()

    time.sleep(3)

    duration = time.perf_counter() - start

    check_latency(duration)


if __name__ == "__main__":

    print("=== NORMAL REQUEST ===")
    normal_request()

    print("\n=== INTENTIONAL REGRESSION ===")
    broken_request()