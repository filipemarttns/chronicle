# Aggregate Roots

Each aggregate enforces invariants inside a transactional boundary. Cross-aggregate consistency is eventual via the event log and projectors, except where a single DB transaction intentionally spans append + outbox (ingest).

---

## Workspace

**Context:** Identity & Access  
**Root id:** `WorkspaceId`

### Invariants

1. Name is non-empty and ≤ 120 characters.
2. Retention and consent policies are always defined (defaults applied on create).
3. Legal hold, when enabled, blocks automated purge jobs for the workspace.
4. Soft-deleted workspaces reject new ingest.

### State

| Field | Type | Notes |
| --- | --- | --- |
| `id` | WorkspaceId | |
| `name` | WorkspaceName | VO |
| `settings` | WorkspaceSettings | retention, idle timeout, feature flags |
| `legal_hold` | bool | |
| `created_at` | Instant | |
| `archived_at` | Instant \| null | |

### Commands

- `CreateWorkspace`
- `UpdateWorkspaceSettings`
- `EnableLegalHold` / `DisableLegalHold`
- `ArchiveWorkspace`

---

## Device

**Context:** Identity & Access  
**Root id:** `DeviceId`  
**Belongs to:** Workspace

### Invariants

1. Device is unique per `(workspace_id, device_fingerprint)` when fingerprint present.
2. Revoked devices cannot ingest.
3. Label is optional but ≤ 80 characters.

### State

| Field | Type |
| --- | --- |
| `id` | DeviceId |
| `workspace_id` | WorkspaceId |
| `label` | DeviceLabel \| null |
| `fingerprint` | DeviceFingerprint \| null |
| `status` | `active` \| `revoked` |
| `registered_at` | Instant |
| `revoked_at` | Instant \| null |

### Commands

- `RegisterDevice`
- `RevokeDevice`
- `RenameDevice`

---

## Credential

**Context:** Identity & Access  
**Root id:** `CredentialId`

### Invariants

1. Secret material is stored hashed (or in a secrets backend); plaintext never persisted in the event log.
2. Expired or revoked credentials fail authz.
3. Scope must include at least one workspace or be explicitly global-admin (rare; self-host single-tenant often workspace-scoped).

### Commands

- `IssueCredential`
- `RotateCredential`
- `RevokeCredential`

---

## ConsentGrant (aggregate per workspace policy document)

**Context:** Identity & Access  
**Root id:** `WorkspaceId` (consent modeled as part of workspace policy **or** separate aggregate `ConsentPolicy`)

**Decision:** Model as **`ConsentPolicy` aggregate** rooted by `WorkspaceId` to keep consent changes explicit and auditable without overloading Workspace settings blobs.

### Invariants

1. Categories are exactly the known set: `editor`, `terminal`, `git`, `browser`, `assistant`, `build`.
2. `browser` and `assistant` default to `false`.
3. Every change emits `ConsentChanged` with actor and timestamp.

---

## Session

**Context:** Session  
**Root id:** `SessionId`

### Invariants

1. `started_at` ≤ `ended_at` when closed.
2. Open sessions have `ended_at = null`.
3. A device may have at most one open session per workspace under algorithm version `v1`.
4. Closing is irreversible; corrections use `SessionMerged` / compensating events.
5. `algorithm_version` is immutable for the session lifetime.

### State

| Field | Type |
| --- | --- |
| `id` | SessionId |
| `workspace_id` | WorkspaceId |
| `device_id` | DeviceId |
| `started_at` | Instant |
| `ended_at` | Instant \| null |
| `algorithm_version` | AlgorithmVersion |
| `last_activity_at` | Instant |

### Commands

- `StartSession` (usually projector/domain service driven)
- `TouchSession` (extend last activity)
- `CloseSession`
- `MergeSessions` (admin/correction)

---

## Event log (store) — not a DDD aggregate in the classical sense

The append-only log is a **domain infrastructure concept** with invariants enforced by `EventStore` + ingest application service:

1. Immutability after append
2. Idempotency uniqueness `(workspace_id, idempotency_key)`
3. Envelope completeness (ADR-0009)

Documented here so implementers do not invent a mutable `Activity` aggregate as source of truth.

---

## MemoryIndex (logical aggregate)

**Context:** Memory & Search  
**Root id:** `WorkspaceId` + `model_id` (logical)

### Invariants

1. Chunks cite one or more event ids or derived document ids.
2. Re-embed creates new vectors tied to `model_id`; old vectors retained until retention/purge.
3. Index rebuild is allowed and must be deterministic given the same chunk set and model.

Commands are application-level (`ReindexWorkspace`, `EmbedChunkBatch`), not user-facing aggregates with rich behavior.

---

## GraphSnapshot (logical)

**Context:** Knowledge Graph  

Rebuild unit for projector version `N`. No client-written edges as durable truth (ADR-0019).

---

## SyncState

**Context:** Sync  
**Root id:** `(WorkspaceId, DeviceId)`

### Invariants

1. Cursor is monotonic (`last_offset` non-decreasing) on successful pull apply.
2. Conflicts never overwrite existing event payloads.
3. Push rejects revoked devices.

### State

| Field | Type |
| --- | --- |
| `workspace_id` | WorkspaceId |
| `device_id` | DeviceId |
| `last_offset` | StoreOffset |
| `last_sync_at` | Instant \| null |
