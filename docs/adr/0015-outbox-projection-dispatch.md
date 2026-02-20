# ADR-0015: Transactional Outbox for Projection Dispatch

- Status: Accepted
- Date: 2026-02-12
- Deciders: Lead Maintainer
- Tags: reliability, workers

## Context

If the API appends an event and then fails to enqueue a Celery task, projections stall silently. Dual-write to database and broker without coordination creates lost or duplicate work under partial failures.

## Decision

Implement the **transactional outbox** pattern:

1. In the same database transaction as the event append, write an outbox row describing the work (e.g., `project_event`, event id, attempt metadata).
2. A publisher process/task reliably drains the outbox to Redis/Celery.
3. Projectors consume jobs idempotently and acknowledge completion.
4. Outbox rows are marked published/processed; retention cleans old rows.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Listen/notify only | Easy to miss under disconnect; weaker durability guarantees |
| Dual-write without outbox | Classic lost-update under crash |
| Polling event table only | Works but outbox clarifies intent and reduces hot scans when designed with indexes |

Polling the event store by offset remains acceptable for rebuilds; outbox optimizes steady-state dispatch.

## Consequences

- Slightly more schema and worker code.
- Operational metrics: outbox lag, publish failures.
- Exactly-once end-to-end is still not claimed; idempotency remains required.

## References

- ADR-0002, ADR-0006
- [diagrams/event-flow.md](../diagrams/event-flow.md)
