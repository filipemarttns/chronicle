# ADR-0005: pgvector for Local Embeddings

- Status: Accepted
- Date: 2026-01-18
- Deciders: Lead Maintainer
- Tags: search, memory, privacy

## Context

Semantic search and AI memory require vector similarity over chunks derived from events, diffs, and documents. Hosted vector databases and remote embedding APIs create privacy and operational coupling that conflict with Chronicle’s local-first default.

## Decision

Store embeddings in **PostgreSQL using pgvector**, in the same operational database as events and SQL projections. Embedding computation runs in workers under operator control (local models by default; remote providers only when explicitly configured).

## Alternatives Considered

| Alternative | Why rejected for default |
| --- | --- |
| Dedicated vector DB (Qdrant, Milvus, etc.) | Extra service for self-hosters; sync complexity |
| Hosted embedding + vector API only | Privacy and dependency concerns for default path |
| Inverted index only (BM25) | Insufficient for natural-language “memory” queries |
| Filesystem vector files | Weak concurrency and transactional coupling |

## Consequences

- One backup domain covers events and vectors (with retention cascading).
- ANN index choice matters (ADR-0014).
- Large corpora may need read replicas or eventual split—domain APIs stay stable.
- Hybrid retrieval (metadata predicates + vectors) is natural in SQL.

## References

- ADR-0014, ADR-0013
- [benchmarks/methodology.md](../benchmarks/methodology.md)
