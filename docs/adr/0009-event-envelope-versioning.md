# ADR-0009: Event Envelope and Schema Versioning

- Status: Accepted
- Date: 2026-01-24
- Deciders: Lead Maintainer
- Tags: events, compatibility

## Context

Capture surfaces evolve independently. Without a strict envelope and versioning rules, projections break, search quality degrades, and historical events become unreadable.

## Decision

Every persisted event uses a standard **event envelope**:

| Field | Purpose |
| --- | --- |
| `event_id` | Globally unique identifier |
| `type` | Dot-namespaced telemetry or domain type string |
| `schema_version` | Integer version of the payload schema for that type |
| `occurred_at` | Producer timestamp (UTC) |
| `received_at` | Server timestamp (UTC) |
| `source` | Capture surface identifier |
| `actor_id` | Authenticated principal |
| `workspace_id` | Isolation scope |
| `device_id` | Device identity |
| `idempotency_key` | Client-supplied dedupe key |
| `correlation_id` / `causation_id` | Trace linkage |
| `payload` | Type-specific JSON object |

Rules:

1. Additive optional fields preferred within a `schema_version`.
2. Breaking payload changes increment `schema_version` and require dual-read in projectors until backfill completes.
3. Consumers ignore unknown fields.
4. Removing or renaming fields requires a migration plan and ADR if semantics change.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Unversioned free-form JSON | Unmaintainable over years |
| Protobuf-only on the wire | Higher friction for extensions; JSON envelope still needed for store |
| One global schema version for all types | Couples unrelated event families |

## Consequences

- Schema registry tests in CI.
- Documentation must list active types and versions.
- Older events remain queryable with version-aware decoders.

## References

- ADR-0001, ADR-0010
- [architecture/event-model.md](../architecture/event-model.md)
