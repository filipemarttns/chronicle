# ADR-0018: Multi-Device Sync Protocol

- Status: Accepted
- Date: 2026-02-25
- Deciders: Lead Maintainer
- Tags: sync, distributed

## Context

Developers work across laptops and desktops. Memory siloed per device fails the product thesis. Naive last-write-wins on projections would diverge from append-only truth.

## Decision

Sync operates on the **event log**, not on mutable projections:

1. Each device has a `device_id` and per-workspace sync cursor.
2. `push` uploads accepted local events (with idempotency keys).
3. `pull` downloads events since cursor.
4. Conflict is defined primarily as idempotency-key payload mismatch or clock pathologies; reported via `ConflictRecord`.
5. After log convergence, each node rebuilds/advances projections locally.

Optional end-to-end encryption for sync transport is a deployment configuration, not a substitute for authz.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Sync only read models | Divergent, unreproducible history |
| CRDTs for all payloads | Overkill for immutable facts; complex semantics |
| Central cloud mandatory | Conflicts with local-first default |

## Consequences

- Projection lag may differ per device after sync.
- Large initial syncs need pagination and backpressure.
- Security review required for sync endpoints (auth, rate limits).

## References

- ADR-0001, ADR-0013
- [diagrams/sequence-sync.md](../diagrams/sequence-sync.md)
