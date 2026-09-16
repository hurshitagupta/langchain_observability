import os
import time

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from prometheus_client import Counter, Histogram, start_http_server

load_dotenv()


model = ChatOpenRouter(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0,
    timeout=30_000,
)

REQUEST_COUNT = Counter("llm_requests_total","Total number of LLM requests")

ERROR_COUNT = Counter("llm_errors_total","Total number of failed LLM requests")

LATENCY = Histogram(
    "llm_request_duration_seconds",
    "Time taken by LLM requests"
)

def observed_model_call(question: str) -> str:

    REQUEST_COUNT.inc()

    start = time.perf_counter()

    try:
        response = model.invoke(question)
        return response.content

    except Exception:
        ERROR_COUNT.inc()
        raise

    finally:
        duration = time.perf_counter() - start

        LATENCY.observe(duration)

        print(f"Recorded latency: {duration:.2f} seconds")

if __name__ == "__main__":

    start_http_server(8000)

    print("Metrics available at http://localhost:8000/metrics")

    answer = observed_model_call(
        "Explain observability in one short sentence."
    )

    print("\nAnswer:")
    print(answer)

    input("\nPress Enter to stop the metrics server...")