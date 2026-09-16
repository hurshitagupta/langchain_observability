# LangChain Observability

This project implements the hands-on assessment for **Topic 16 — Observability**.

## Task 1 — Structured Logging

Task 1 implements structured JSON logging for a real LLM request using `ChatOpenRouter`.

Each model request generates a JSON log containing:

- `request_id` — unique ID generated for every request
- `step` — the operation being observed
- `duration_ms` — time taken by the model call in milliseconds
- `tokens` — total input and output tokens used
- `outcome` — whether the request was successful or failed

### Implementation

The model is called using `ChatOpenRouter`.

A unique request ID is generated using `uuid.uuid4()` and the request duration is measured using `time.perf_counter()`.

Token usage is taken from the model response `usage_metadata`:

```python
usage = response.usage_metadata or {}

input_tokens = usage.get("input_tokens", 0)
output_tokens = usage.get("output_tokens", 0)

tokens = input_tokens + output_tokens
```

A `try/except/finally` block is used so that a structured log is generated for both successful and failed requests.

The final log is converted to JSON using `json.dumps()` and written using Python's `logging` module.

### Run Task 

```bash
uv run python -m structured_logging.structured_logging
```

## Automated Tests

Run Tests

```bash
uv run pytest tests/test_structured_logging.py -v
```

## Evidence

Save the Task 1 execution output:

```bash
uv run python -m structured_logging.structured_logging > outputs/structured_logging.txt 2>&1
```

Save the automated test output:

```bash
uv run pytest tests/test_structured_logging.py -v > outputs/test_structured_logging.txt 2>&1
```