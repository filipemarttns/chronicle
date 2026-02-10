# ADR-0004: PostgreSQL as Event Store

- Status: Accepted
- Date: 2026-01-18
- Deciders: Lead Maintainer
- Tags: storage, persistence

## Context

Chronicle needs transactional appends, idempotency constraints, relational projections, SQL operability for self-hosters, and a single operational database story for early milestones. Exotic event-store products add learning cost and weaken the “docker compose up” experience.

## Decision

Use **PostgreSQL** as the primary event store and as the home for SQL read models. Store event payloads in `JSONB` with explicit schema version columns. Use Alembic for migrations.

pgvector (ADR-0005) extends the same database for embeddings.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| EventStoreDB / Kafka as primary store | Extra moving parts; weaker fit for single-node local-first |
| SQLite only | Insufficient for concurrent workers and vector workloads at target scale |
| Document DB as system of record | Weaker transactional story for outbox + constraints |
| Pure object storage log | Poor queryability and idempotency enforcement |

## Consequences

- Operators already know how to back up and restore Postgres.
- Partitioning and vacuum strategies become part of capacity planning.
- Very high multi-tenant SaaS scale may later justify streaming log specialization—without changing the domain event model.
- JSONB payload size and indexing require explicit guidelines.

## References

- ADR-0001, ADR-0005, ADR-0015
- [deployment/capacity-planning.md](../deployment/capacity-planning.md)
