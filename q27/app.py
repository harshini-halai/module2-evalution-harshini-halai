import logging
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from guardrails import check_query, llm_policy_check
from llm_client import get_llm_client

# Logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# FastAPI
app = FastAPI(title="Northwind Freight Chat Service")

llm = get_llm_client()

# Prometheus metrics
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["method", "path"],
)

LLM_LATENCY = Histogram(
    "llm_latency_seconds",
    "LLM request latency",
)

PROMPT_TOKENS = Counter(
    "llm_prompt_tokens_total",
    "Total prompt tokens",
)

COMPLETION_TOKENS = Counter(
    "llm_completion_tokens_total",
    "Total completion tokens",
)

LLM_COST = Counter(
    "llm_cost_usd_total",
    "Cumulative LLM cost in USD",
)

GUARDRAIL_BLOCKS = Counter(
    "guardrail_blocks_total",
    "Total guardrail blocks",
    ["layer", "reason"],
)

ERRORS = Counter(
    "errors_total",
    "Total errors",
    ["type"],
)

IN_FLIGHT = Gauge(
    "requests_in_flight",
    "Requests currently being processed",
)

# Middleware

@app.middleware("http")
async def metrics_middleware(request, call_next):

    start_time = time.time()
    IN_FLIGHT.inc()

    try:
        response = await call_next(request)

        status = str(response.status_code)

        HTTP_REQUESTS.labels(
            request.method,
            request.url.path,
            status,
        ).inc()

        return response

    except Exception as exc:

        ERRORS.labels(type(exc).__name__).inc()
        logger.exception("Request failed")

        raise

    finally:

        elapsed = time.time() - start_time

        HTTP_LATENCY.labels(
            request.method,
            request.url.path,
        ).observe(elapsed)

        IN_FLIGHT.dec()

# Health endpoint
@app.get("/")
def root():
    return {
        "service": "Northwind Freight Chat Service",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

# Metrics endpoint
@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }

# Chat endpoint
@app.post("/chat")
def chat(query: str):

    logger.info("Chat request received")

    # Layer 1: deterministic guardrail
    deterministic_result = check_query(query)

    if not deterministic_result["valid"]:

        GUARDRAIL_BLOCKS.labels(
            "deterministic",
            deterministic_result["reason"],
        ).inc()

        logger.info(
            "Request blocked by deterministic guardrail: %s",
            deterministic_result["reason"],
        )

        return JSONResponse(
            status_code=400,
            content=deterministic_result,
        )

    # Layer 2: LLM-as-judge
    judge_start = time.time()

    judge_result = llm_policy_check(query)

    LLM_LATENCY.observe(time.time() - judge_start)

    if not judge_result["valid"]:

        GUARDRAIL_BLOCKS.labels(
            "llm_judge",
            judge_result["reason"],
        ).inc()

        logger.info(
            "Request blocked by LLM judge: %s",
            judge_result["reason"],
        )

        return JSONResponse(
            status_code=400,
            content=judge_result,
        )

    # Actual LLM response
    try:
        llm_start = time.time()

        response = llm.generate(query)

        LLM_LATENCY.observe(time.time() - llm_start)

        usage = getattr(llm, "last_usage", {})

        PROMPT_TOKENS.inc(usage.get("prompt_tokens", 0))
        COMPLETION_TOKENS.inc(usage.get("completion_tokens", 0))
        LLM_COST.inc(usage.get("cost_usd", 0.0))

        return {
            "valid": True,
            "response": response,
        }

    except Exception as exc:
        ERRORS.labels(type(exc).__name__).inc()

        logger.exception("LLM request failed")

        return JSONResponse(
            status_code=500,
            content={
                "valid": False,
                "reason": "Internal LLM error",
            },
        )