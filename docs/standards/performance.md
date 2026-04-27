# Performance Standards

## Design targets

Published in README and [docs/benchmarks/targets.md](../benchmarks/targets.md). Treat as engineering budgets:

| Workload | Budget |
| --- | --- |
| Batched ingest | ≥ 5,000 events/s on single-site profile |
| Embed (CPU baseline) | ≥ 200 chunks/s |
| Search p95 | ≤ 120 ms @ 1M vectors, k=10 |
| Replay 1h session | ≤ 250 ms |
| Ingest ack p95 (local) | ≤ 50 ms |

## Engineering rules

1. **Ingest path stays thin** — no synchronous embedding or graph fan-out in the request transaction beyond outbox write
2. **Batch where possible** — clients and workers prefer batches
3. **Index deliberately** — every new query shape needs an index plan
4. **Measure before claiming** — no perf claims without benchmark numbers
5. **Avoid N+1** in projectors and API hydrations
6. **Bound work** — graph depth limits, search `k` caps, batch max 500

## PR requirements for perf-sensitive changes

Changes touching ingest, search, projection, or sync must include:

- Before/after measurements **or** reasoned explanation why perf is unaffected
- Notes on lock/contention risk
- Queue isolation impact (if any)

Regressions >20% on gated suites vs previous RC need maintainer acknowledgement ([docs/benchmarks/targets.md](../benchmarks/targets.md)).

## Allocation and footprint

- Desktop/tray app must remain lightweight (justifies Tauri choice)
- Extensions must bound offline buffers (size + age)
- Embed workers should configure batch sizes explicitly—no unbounded memory growth

## Profiling

Use sampling profilers on representative synthetic loads. Commit flamegraph artifacts only when small and useful; otherwise link from the PR.

## Caching

Caches are optimization, not source of truth. Cache keys must include workspace scope. TTL and invalidation strategy documented when introduced.
