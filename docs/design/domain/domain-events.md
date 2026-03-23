# Domain Events

Domain events express **aggregate and policy transitions**. They are distinct from capture telemetry types (see [../events/catalog.md](../events/catalog.md)), though both may be persisted in the same event log with different `type` namespaces.

Convention:

- Telemetry: `editor.*`, `terminal.*`, `git.*`, …
- Domain: `chronicle.domain.*` (or short `domain.*` — **normative prefix: `domain.`**)

## Catalog

### Identity & Access

| Type | schema_version | Payload (salient) | When |
| --- | --- | --- | --- |
| `domain.workspace.created` | 1 | `name`, `settings` | Workspace created |
| `domain.workspace.settings_updated` | 1 | `changed_keys`, `settings` | Settings change |
| `domain.workspace.archived` | 1 | `reason?` | Archive |
| `domain.device.registered` | 1 | `device_id`, `label?`, `fingerprint?` | Device register |
| `domain.device.revoked` | 1 | `device_id`, `reason?` | Revoke |
| `domain.credential.issued` | 1 | `credential_id`, `scopes` (no secret) | Issue token |
| `domain.credential.rotated` | 1 | `credential_id` | Rotate |
| `domain.credential.revoked` | 1 | `credential_id` | Revoke |
| `domain.consent.changed` | 1 | `category`, `enabled`, `actor_id` | Consent toggle |

### Capture

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.event.accepted` | 1 | `event_id`, `telemetry_type`, `store_offset` | After durable append of telemetry (optional mirror; projectors may use telemetry directly) |
| `domain.event.rejected` | 1 | `reason_code`, `idempotency_key?` | Audit-only; may live in audit log instead of event store |

**Implementation note:** Prefer projecting from telemetry envelopes directly. Emit `domain.event.accepted` only if cross-context notifications require it without coupling to telemetry schemas.

### Session

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.session.started` | 1 | `session_id`, `device_id`, `started_at`, `algorithm_version` | Session opens |
| `domain.session.closed` | 1 | `session_id`, `ended_at`, `reason` (`idle`\|`explicit`\|`workspace_switch`) | Session closes |
| `domain.session.merged` | 1 | `target_session_id`, `source_session_ids[]` | Correction |

### Memory

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.memory.chunks_embedded` | 1 | `chunk_ids[]`, `model_id`, `count` | Embed batch done |
| `domain.memory.reindex_completed` | 1 | `model_id`, `chunk_count` | Reindex finished |

### Graph

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.graph.projected` | 1 | `projector_version`, `through_offset` | Checkpoint advance (may be sparse) |

### Analytics

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.analytics.window_closed` | 1 | `metric_name`, `window_start`, `window_end`, `values` | Window finalize |

### Sync

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.sync.batch_applied` | 1 | `device_id`, `count`, `through_offset` | Pull applied |
| `domain.sync.conflict_detected` | 1 | `conflict_id`, `idempotency_key` | Conflict recorded |

### Automation

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.mcp.tool_invoked` | 1 | `invocation_id`, `tool`, `actor_id` (args hashed) | MCP tool call |

### Retention

| Type | schema_version | Payload | When |
| --- | --- | --- | --- |
| `domain.retention.purged` | 1 | `scope`, `event_count`, `chunk_count` | Purge completed |

## Delivery

Domain events are appended to the event log (same store) **or** recorded in an audit table when they must not inflate telemetry streams. Normative choice for Chronicle:

- **Session, consent, sync conflict, retention, credential lifecycle** → event log
- **MCP tool invocation** → audit table + optional domain event summary
- **Projector checkpoints** → projector checkpoint table (not necessarily event log)

Document the choice in code modules to avoid dual writes without need.
