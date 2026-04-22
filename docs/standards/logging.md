# Logging Standards

## Format

JSON logs to stdout (Twelve-Factor). One event per line.

### Required fields

| Field | Description |
| --- | --- |
| `timestamp` | ISO-8601 UTC |
| `level` | `debug` \| `info` \| `warning` \| `error` |
| `message` | Human-readable, concise |
| `component` | `api`, `worker.timeline`, `worker.embed`, `mcp`, … |
| `correlation_id` | Propagated across request/job |

### Conditional fields

| Field | When |
| --- | --- |
| `workspace_id` | Known and safe |
| `event_id` | Event-specific handling |
| `store_offset` | Projection progress |
| `error_type` | Exceptions |
| `duration_ms` | Timed operations |

## Levels

| Level | Use |
| --- | --- |
| `debug` | Development detail; disabled by default in production |
| `info` | Normal operations (ingest accepted, projector checkpoint) |
| `warning` | Recoverable anomalies (retry, lag high) |
| `error` | Failures needing attention |

## Prohibited content

- Secrets, tokens, passwords
- Full event payloads (log type + id instead)
- Raw browser URLs with credentials
- Authorization headers
- Entire AI prompts/responses

## Correlation

- Accept `X-Correlation-Id` or generate UUIDv7
- Pass into Celery job headers/kwargs
- Return in API error bodies (`correlation_id`)

## Sampling

High-volume debug logs (e.g., every selection event) must be sampled or omitted. Prefer metrics for volume signals.
