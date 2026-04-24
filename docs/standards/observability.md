# Observability Standards

Implements ADR-0020. Operational naming lives also in [docs/deployment/observability.md](../deployment/observability.md).

## Pillars

1. **Logs** — structured, correlatable ([logging.md](logging.md))
2. **Metrics** — RED/USE-ish signals for ingest, queues, search
3. **Traces** — request → worker job correlation where supported
4. **Audit** — consent, export, purge, MCP (separate from debug logs)

## Required metrics for core paths

| Area | Metrics |
| --- | --- |
| Ingest | `chronicle_events_appended_total`, `chronicle_ingest_ack_latency_seconds` |
| Outbox | `chronicle_outbox_lag_seconds` |
| Projection | `chronicle_projection_lag_seconds{projector=}` |
| Embed | `chronicle_embed_queue_depth`, embed latency histogram |
| Search | `chronicle_search_latency_seconds` |
| Sync | `chronicle_sync_push_total`, pull totals |
| Security | `chronicle_auth_failures_total`, `chronicle_redactions_total` |

## Cardinality rules

Forbidden as metric labels:

- file paths
- raw URLs
- event payloads
- user display names
- idempotency keys

Allowed: `projector`, `event_family`, `workspace_id` only if cardinality is controlled (prefer hashes or omit in large multi-tenant futures).

## Health endpoints

| Endpoint | Meaning |
| --- | --- |
| `/health` | Process up |
| `/ready` | Postgres (and Redis if required for writes) reachable |

Do not overload `/health` with dependency checks.

## Continuous improvement

New failure modes in a PR should add at least one metric or structured log field that makes the failure diagnosable in production.
