# CQRS and Event Sourcing Mechanics

## Write path

1. Authenticate request
2. Enforce workspace policy and consent
3. Redact payload
4. Validate envelope + type schema
5. Append event + outbox in one transaction
6. Return event id

## Read path

1. Authenticate and authorize
2. Query the appropriate read model
3. Apply response redaction if needed
4. Return DTOs with citation ids

## Projector contract

Every projector implements:

| Method | Behavior |
| --- | --- |
| `name` | Stable projector identity |
| `version` | Increments on incompatible logic changes |
| `apply(event)` | Idempotent mutation of read model |
| `checkpoint` | Last applied `store_offset` |

Rebuilding: reset checkpoint + truncate projector-owned tables + replay.

## Consistency model

- **Strong** for “event accepted” durability after 201/200 ack
- **Eventual** for timeline/search/graph freshness
- **Causal** within a device’s local stream after sync pull apply order

## Failure playbooks (summary)

| Symptom | Action |
| --- | --- |
| Outbox lag rising | Scale publishers/workers; check Redis |
| Projector errors | Quarantine poison event; patch projector; resume |
| Search stale | Check embed queue; verify model health |

Details: [../deployment/disaster-recovery.md](../deployment/disaster-recovery.md).
