# ADR-0020: Observability Standards

- Status: Accepted
- Date: 2026-03-04
- Deciders: Lead Maintainer
- Tags: ops, observability

## Context

Projection lag, ingest failures, and embed backlogs are otherwise invisible. Operators need a consistent telemetry model across API and workers.

## Decision

Adopt these standards:

1. **Structured JSON logs** with `correlation_id`, `workspace_id` (when safe), `event_id` (when relevant), severity, and component.
2. **Metrics**: ingest_ack_latency, events_appended_total, outbox_lag_seconds, projection_lag_seconds, embed_queue_depth, search_latency_ms, sync_push_total, auth_failures_total.
3. **Tracing**: propagate trace context from HTTP into worker jobs where instrumentation allows.
4. **Audit log** distinct from debug logs for consent, export, purge, and MCP tool use.
5. **Health/readiness** endpoints separate liveness from dependency readiness (Postgres, Redis).

Metric names use a `chronicle_` prefix. High-cardinality labels (raw file paths, URLs) are forbidden.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Ad-hoc print debugging | Unoperable |
| Traces only | Insufficient for capacity and lag SLOs |
| Log every payload | Privacy and volume hazard |

## Consequences

- Docs and dashboards reference the same metric names.
- PRs adding features should add metrics/logs when new failure modes appear.
- Default Compose may include optional OTLP endpoints as the stack matures.

## References

- [deployment/observability.md](../deployment/observability.md)
