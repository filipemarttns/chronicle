# ADR-0014: HNSW as Default Vector Index

- Status: Accepted
- Date: 2026-02-12
- Deciders: Lead Maintainer
- Tags: search, performance

## Context

pgvector supports multiple index types. Chronicle’s interactive search UX needs low-latency approximate nearest neighbor queries over developer-scale corpora (10^5–10^7 chunks on single-node profiles).

## Decision

Use **HNSW** as the default ANN index for embedding tables in pgvector. Document IVFFlat as an alternative for memory-constrained environments or bulk-load-then-query workflows.

Index build parameters ship with documented defaults and are tunable per deployment.

## Alternatives Considered

| Alternative | Trade-off |
| --- | --- |
| IVFFlat default | Lower memory; often higher latency / more tuning for interactive UX |
| Exact search only | Won’t meet p95 targets at design corpus sizes |
| External ANN service | Violates single-DB preference without strong need |

## Consequences

- Higher RAM for large HNSW graphs—capacity planning must account for it.
- Re-embed jobs may require careful reindexing procedures.
- Benchmarks must publish recall@k alongside latency.

## References

- ADR-0005
- [benchmarks/methodology.md](../benchmarks/methodology.md)
- [deployment/capacity-planning.md](../deployment/capacity-planning.md)
