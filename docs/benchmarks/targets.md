# Performance Targets

Design targets for capacity planning and release gates. Not yet claimed as measured production numbers.

| Workload | Target | Gate |
| --- | --- | --- |
| Event ingest sync | ≥ 5,000 events/s batched on `single-site` | RC minor |
| Embedding throughput | ≥ 200 chunks/s CPU baseline | RC minor |
| Semantic search p95 | ≤ 120 ms @ 1M vectors, k=10 | RC minor |
| Timeline reconstruct (1h) | ≤ 250 ms | RC minor |
| Knowledge graph 2-hop | ≤ 80 ms | aspirational until graph ships |
| Ingest ack p95 (local) | ≤ 50 ms | continuous |

Release candidates that regress >20% on gated suites vs previous RC require maintainer acknowledgement in the release PR.

Release managers may waive a gate only with written rationale in the release PR.

