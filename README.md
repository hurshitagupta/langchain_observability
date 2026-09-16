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

---

## Task 2 — Tracing

Task 2 implements tracing with LangSmith and propagates a correlation ID across the request.

The traced request contains three main operations:

- Retriever call
- Tool call
- Model call

A unique correlation ID is generated for each request using `uuid`.

The same correlation ID is added to the metadata of the retriever, tool, and model calls so that operations belonging to the same request can be identified together.

### LangSmith Tracing

LangSmith tracing is enabled using environment variables.

Secrets are stored in `.env` and are not hardcoded in the source code.

The `@traceable` decorator is used for custom Python functions that should appear in LangSmith traces.

The retriever is traced as:

```python
@traceable(
    name="retrieve_documents",
    run_type="retriever"
)
```

The complete request is also wrapped using:

```python
@traceable(name="observability_request")
```

LangChain components such as the tool and model receive the correlation ID through `config` metadata.

This allows the same request ID to be associated with the operations performed during the request.

### Run Task 2

```bash
uv run python -m tracing.tracing
```

### Automated Tests

Run Tests

```bash
uv run pytest tests/test_tracing.py -v
```

### Evidence

Save the Task 2 execution output:

```bash
uv run python -m tracing.tracing > outputs/tracing.txt 2>&1
```

Save the automated test output:

```bash
uv run pytest tests/test_tracing.py -v > outputs/test_tracing.txt 2>&1
```

The LangSmith trace provides additional evidence showing the traced request and its associated operations.

---

## Task 3 — Redaction

Task 3 implements redaction to prevent sensitive information from reaching application logs.

The implementation currently protects:

- Email addresses
- API-key-like values beginning with `sk-`

Regular expressions are used to detect sensitive values before the message is logged.

### Run Task 3

```bash
uv run python -m redaction.redaction
```

## Automated Tests

Task 3 includes automated checks for redaction and leakage detection.

The success test passes sensitive information through `safe_log()` and verifies that the original email address and API key do not appear in the generated log.

It also verifies that the expected redaction markers are present.

The leakage detection test intentionally provides unredacted sensitive information and verifies that the configured patterns can detect it.

### Run Tests

```bash
uv run pytest tests/test_redaction.py -v
```

### Evidence

Save the redaction output:

```bash
uv run python -m redaction.redaction > outputs/redaction.txt 2>&1
```

Save the automated test output:

```bash
uv run pytest tests/test_redaction.py -v > outputs/test_redaction.txt 2>&1
```

---

## Task 4 — Metrics and Dashboard

Task 4 implements application metrics using the Prometheus Python client.

The implementation tracks three metrics:

- `llm_requests_total` — total number of LLM requests
- `llm_errors_total` — total number of failed LLM requests
- `llm_request_duration_seconds` — histogram containing LLM request latency

### Request Counter

A Prometheus `Counter` is used to track the total number of model requests.

```python
REQUEST_COUNT.inc()
```

The request counter increases whenever an LLM request starts.

### Error Counter

A separate counter tracks failed model requests.

```python
except Exception:
    ERROR_COUNT.inc()
    raise
```

The error counter only increases when a model request fails.

### Latency Histogram

The execution time of each model request is measured using `time.perf_counter()`.

```python
start = time.perf_counter()
```

After the request completes, the duration is calculated and added to the Prometheus histogram.

```python
duration = time.perf_counter() - start
LATENCY.observe(duration)
```

Latency is recorded inside the `finally` block so that it is measured for both successful and failed requests.

### Metrics Endpoint

Prometheus metrics are exposed using:

```python
start_http_server(8000)
```

This starts a metrics server on port `8000`.

The metrics can be viewed or scraped from:

```text
http://localhost:8000/metrics
```

The application is kept running after the model request so that the metrics endpoint can be inspected.

### Run Task 4

```bash
uv run python -m metrics_and_dashboard.metrics_and_dashboard
```

After the model request completes, the terminal displays the measured latency.

### Automated Tests

Task 4 includes automated tests for both successful and failed model requests.

### Run Tests

```bash
uv run pytest tests/test_metrics_and_dashboard.py -v
```

### Evidence

The Prometheus metrics scrape is saved in:

```text
outputs/metrics_and_dashboard.txt
```

The automated test evidence is saved in:

```text
outputs/test_metrics_and_dashboard.txt
```

The scrape output provides evidence that the request counter, error counter, and latency histogram are successfully exposed.