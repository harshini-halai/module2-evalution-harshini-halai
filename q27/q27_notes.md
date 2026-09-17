# Q27 Notes

## Assigned Domain

Logistics — Northwind Freight shipment tracking assistant.

## Guardrail Design

The request passes through two guardrail stages in this order:

1. Deterministic filter
   - Banned keywords
   - Competitor mentions
   - PII detection using email and phone-number patterns

2. LLM-as-judge policy check
   - Loads the assigned policy from policy/domain.md
   - Sends the policy and user query to the LLM
   - Requires JSON with valid and reason
   - Validates the response using Pydantic

The LLM judge uses a fail-closed approach. If the judge fails or returns malformed JSON, the request is blocked.

## Provider Abstraction

LLMClient is the common interface.

Implementations:

- MockLLMClient — used for offline tests
- RealLLMClient — used with an OpenAI-compatible provider

The provider is selected using the LLM_PROVIDER environment variable.

Tests use the mock provider, so they require no API key and no network access.

## Monitoring

### Counters

Counters are used for:

- HTTP request count
- Prompt tokens
- Completion tokens
- Cumulative LLM cost
- Guardrail blocks
- Errors

### Histograms

Histograms are used for:

- HTTP request latency
- LLM latency

The LLM latency histogram allows p95 latency to be calculated.

### Gauge

A Gauge is used for requests currently in flight because the value can increase and decrease.

## Middleware

HTTP request metrics are collected through FastAPI middleware instead of duplicating HTTP instrumentation inside every handler.

## Cost Tracking

Prompt and completion tokens are tracked separately.

For the real provider, token usage is read from the provider response and cost is calculated using configurable cost-per-1K-token environment variables.

The mock provider reports zero tokens and zero cost because it does not make a billed model request.

## Prometheus

Prometheus scrapes:

app:8000/metrics

Inside the Docker Compose network, app is the hostname of the FastAPI service.

## PromQL Queries

### Request rate

sum(rate(http_requests_total[5m])) by (status)

### p95 LLM latency

histogram_quantile(0.95, sum(rate(llm_latency_seconds_bucket[5m])) by (le))

### Guardrail blocks

sum by (layer, reason) (guardrail_blocks_total)

## Security

API keys are read from environment variables.

Real API keys must not be committed to Git.

.env.example can contain placeholder configuration.

## Evidence

load_test.py contains a realistic mix of allowed and blocked queries.

metrics_output.txt contains raw output from the /metrics endpoint.

Pytest result: 4 passed.

Docker Compose configuration includes:

- FastAPI application
- Prometheus
- Grafana