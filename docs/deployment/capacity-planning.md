# Capacity Planning

## Design point (single-node)

Assumptions for planning targets published in the README:

| Input | Assumption |
| --- | --- |
| Active developers | 1–25 |
| Events per developer per day | 20k–80k (with editor signals) |
| Avg event payload | 0.5–2 KB after redaction |
| Chunks per day | 5k–40k |
| Embedding dims | 384–1024 |

## Storage estimator

```
event_storage ≈ events_per_day * days_retained * avg_bytes * 1.4  (index overhead)
vector_storage ≈ chunks_retained * dims * 4 bytes * 1.5  (HNSW overhead factor rough)
```

Example: 10 developers × 40k events/day × 180 days × 1 KB × 1.4 ≈ **100 GB** order-of-magnitude for events before compression/partition strategies.

Recompute with measured averages after onboarding.

## Compute estimator

| Workload | Rule of thumb |
| --- | --- |
| API | 2 vCPU / 2 GB per 2–3k ingest events/s batched |
| Timeline workers | 1 worker process per ~1–2k events/s project |
| Embed workers | Bound by model; measure tokens/s on target hardware |
| Postgres | Start 4 vCPU / 16 GB RAM for team single-site; grow with HNSW |

## SLOs to size against

| SLO | Design target |
| --- | --- |
| Ingest ack p95 | ≤ 50 ms local network excluding client |
| Projection lag p95 | ≤ 30 s under normal load |
| Search p95 | ≤ 120 ms at 1M vectors (design) |
| Replay 1h session | ≤ 250 ms projected |

If measured lag exceeds SLO for 15 minutes, scale workers before scaling API.

## Growth triggers

| Signal | Action |
| --- | --- |
| Disk > 70% | Expand volume; review retention |
| Outbox lag rising | Scale publishers/workers |
| Redis memory high | Inspect queue backlog; split queues |
| Search p95 regresses | Reindex, replica, or reduce k / filters |
