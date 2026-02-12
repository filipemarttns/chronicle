# ADR-0006: Redis and Celery for Async Workers

- Status: Accepted
- Date: 2026-01-20
- Deciders: Lead Maintainer
- Tags: workers, async, infrastructure

## Context

Projections, embeddings, graph updates, retention jobs, and sync merges must not block ingest acknowledgements. Chronicle needs a battle-tested task queue that Python teams can operate, with visibility into retries and failures.

## Decision

Use **Redis** as broker/cache/rate-limit store and **Celery** as the worker runtime for asynchronous jobs. Critical “event accepted → enqueue projection” coupling uses a transactional outbox (ADR-0015) rather than fire-and-forget publish inside the request handler alone.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Inline background tasks in the API process | Lost on crash; poor isolation |
| Kafka + custom consumers | Heavier ops for default self-host |
| RQ only | Adequate for tiny jobs; weaker ecosystem for scheduled/complex workflows |
| Cloud-only queues | Conflicts with local-first default |

## Consequences

- Compose stack includes Redis; operators must size memory for queues.
- Workers must be idempotent; at-least-once delivery is assumed.
- Celery version upgrades require CI compatibility tests.
- Rate limiting and short-lived caches share Redis carefully namespaced.

## References

- ADR-0002, ADR-0015
