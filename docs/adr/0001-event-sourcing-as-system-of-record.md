# ADR-0001: Event Sourcing as System of Record

- Status: Accepted
- Date: 2026-01-14
- Deciders: Lead Maintainer
- Tags: domain, persistence, timeline

## Context

Chronicle must reconstruct engineering sessions months or years after they occurred, answer historical debugging questions with evidence, and support auditability of consent and retention actions. A mutable “current state” database alone cannot prove what happened; overwrites destroy the ability to replay.

## Decision

Use **event sourcing** for durable facts: every accepted capture signal and every domain-significant state transition is appended to an immutable event log. Sessions, timelines, search indexes, and the knowledge graph are **projections** derived from that log.

The event log is the system of record. Read models may be deleted and rebuilt.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| CRUD session/activity tables | Loses history; replay becomes guesswork |
| Change-data-capture from git only | Misses editor, terminal, browser, and AI signals |
| External log store only (e.g., object storage events) | Weak transactional coupling to acknowledgements and idempotency |

## Consequences

- Ingest path prioritizes append durability and idempotency.
- Schema evolution of event payloads must be versioned (see ADR-0009).
- Operators gain rebuildability at the cost of projection operational complexity.
- Storage grows with activity volume; retention policies become mandatory (see security retention docs).

## References

- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- ADR-0002, ADR-0009, ADR-0015
