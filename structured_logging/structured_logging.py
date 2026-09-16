import json
import logging
import os
import time
import uuid

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

logger = logging.getLogger("observability")

model = ChatOpenRouter(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0,
    timeout=30_000,
)

def observed_invoke(question: str) -> str:
    request_id = str(uuid.uuid4())[:8]

    start = time.perf_counter()

    tokens = 0

    try:
        response = model.invoke(question)

        usage = response.usage_metadata or {}

        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        tokens = input_tokens + output_tokens

        outcome = "success"

        return response.content

    except Exception:
        outcome = "failure"
        raise

    finally:
        duration_ms = round((time.perf_counter() - start) * 1000,2)

        log_data = {
            "request_id": request_id,
            "step": "model_call",
            "duration_ms": duration_ms,
            "tokens": tokens,
            "outcome": outcome,
        }

        logger.info(json.dumps(log_data))


if __name__ == "__main__":
    answer = observed_invoke(
        "Explain observability in one short sentence."
    )

    print("\nAnswer:")
    print(answer)