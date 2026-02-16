# ADR-0010: Idempotent Ingestion Semantics

- Status: Accepted
- Date: 2026-01-24
- Deciders: Lead Maintainer
- Tags: ingest, reliability

## Context

Capture clients retry on network failure. Without idempotency, retries duplicate events, inflate timelines, and corrupt analytics and embeddings.

## Decision

Require an **idempotency key** on ingest (per workspace). The event store enforces uniqueness on `(workspace_id, idempotency_key)`.

Behavior:

- First successful append returns `201` with the event id.
- Duplicate key with identical payload fingerprint returns `200` with the original event id.
- Duplicate key with conflicting payload returns `409 Conflict`.

Batch ingest applies the same rules per item and returns per-item statuses.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Deduplicate only by event_id client-generated | Clients may regenerate ids on retry incorrectly |
| Time-window fuzzy dedupe | Non-deterministic; hides real bursts |
| Exactly-once broker magic | Not achievable end-to-end across client retries |

## Consequences

- Clients must stably compute idempotency keys (e.g., hash of source identity + logical action id).
- Unique indexes grow; monitor index bloat.
- Exactly-once *processing* still relies on idempotent projectors (at-least-once delivery).

## References

- ADR-0004, ADR-0009
- [api/overview.md](../api/overview.md)
