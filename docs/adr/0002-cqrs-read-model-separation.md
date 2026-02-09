# ADR-0002: CQRS Read-Model Separation

- Status: Accepted
- Date: 2026-01-14
- Deciders: Lead Maintainer
- Tags: domain, query, performance

## Context

Ingestion requires low acknowledgement latency, strong idempotency, and simple write transactions. Query workloads—timeline replay, semantic search, graph traversal, analytics—need denormalized shapes, specialized indexes, and different scaling characteristics.

A single normalized model optimized for both write and read would force unacceptable compromises on either path.

## Decision

Adopt **CQRS**:

- **Write side:** validate and append events (and minimal write-side aggregates such as Session lifecycle commands).
- **Read side:** asynchronous projectors maintain timeline, session summaries, embeddings, graph, and analytics tables.

Query APIs read only from read models (or from the event store for rare administrative rebuild/debug paths).

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Synchronous update of all read models in the ingest transaction | Couples ingest latency to embedding and graph work |
| Shared tables with heavy indexing for both paths | Write amplification and lock contention |
| Separate search database as sole query store | Breaks unified operational story; still need SQL projections |

## Consequences

- Projection lag is an explicit SLO, not a bug by itself.
- Projectors must be idempotent and resumable from offsets.
- Clients must tolerate briefly stale search/timeline results after ingest.
- Monitoring of queue depth and projector lag is mandatory (ADR-0020).

## References

- ADR-0001, ADR-0015, ADR-0014
