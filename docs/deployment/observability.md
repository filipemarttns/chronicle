# Observability

Implements ADR-0020.

## Logs

JSON logs with:

- `timestamp`, `level`, `component`, `message`
- `correlation_id`
- `workspace_id` when safe
- `event_id` when relevant

Do not log raw payloads containing potential secrets.

## Metrics (canonical names)

| Metric | Type | Intent |
| --- | --- | --- |
| `chronicle_ingest_ack_latency_seconds` | histogram | Ack latency |
| `chronicle_events_appended_total` | counter | Throughput |
| `chronicle_outbox_lag_seconds` | gauge | Dispatch health |
| `chronicle_projection_lag_seconds` | gauge | Per projector |
| `chronicle_embed_queue_depth` | gauge | Backlog |
| `chronicle_search_latency_seconds` | histogram | Query UX |
| `chronicle_sync_push_total` | counter | Sync volume |
| `chronicle_auth_failures_total` | counter | Security signal |
| `chronicle_redactions_total` | counter | Detector activity |

## Tracing

Propagate W3C trace context across HTTP; include job ids in worker spans.

## Alerts (suggested)

| Alert | Condition |
| --- | --- |
| Ingest down | success rate collapse |
| Outbox lag | lag > 5m for 10m |
| Projection lag | lag > 15m for 10m |
| Disk | > 80% |
| Auth failures | spike vs baseline |

## Dashboards

Compose may later ship Grafana dashboards as optional profiles. Metric names above remain stable regardless of visualization.
