# Entities

Entities have identity independent of attribute values. Aggregate roots are entities; this document lists **non-root entities** and supporting identities living inside aggregates or read models.

## Inside Identity & Access

| Entity | Identity | Parent | Notes |
| --- | --- | --- | --- |
| `Actor` | `ActorId` | referenced by Workspace membership | Human or service principal |
| `WorkspaceMembership` | `(WorkspaceId, ActorId)` | Workspace | Role: `owner`, `member`, `viewer` |
| `ConsentCategoryState` | `(WorkspaceId, ConsentCategory)` | ConsentPolicy | Enabled flag + updated_at |

## Inside Capture path (transient)

| Entity | Identity | Notes |
| --- | --- | --- |
| `IngestItem` | position in batch + idempotency key | Transient during batch processing; not persisted as entity table |

## Inside Session context

| Entity | Identity | Notes |
| --- | --- | --- |
| `SessionAssignment` | `(EventId, SessionId)` | Projection/assignment record; may live in read model |

## Inside Memory context

| Entity | Identity | Notes |
| --- | --- | --- |
| `MemoryChunk` | `ChunkId` | Content + citations; embedding is related VO/record |
| `EmbeddingRecord` | `ChunkId` + `model_id` | Vector row |

## Inside Knowledge Graph

| Entity | Identity | Notes |
| --- | --- | --- |
| `GraphNode` | `NodeId` | Also has unique `(workspace_id, node_type, external_key)` |
| `GraphEdge` | `EdgeId` | Endpoints + type |
| `GraphEvidence` | `(EdgeId, EventId)` | Explainability |

## Inside Analytics

| Entity | Identity | Notes |
| --- | --- | --- |
| `MetricSample` | `(WorkspaceId, MetricName, WindowStart)` | Aggregated bucket |

## Inside Sync / Audit

| Entity | Identity | Notes |
| --- | --- | --- |
| `ConflictRecord` | `ConflictId` | Idempotency mismatch evidence |
| `ToolInvocation` | `InvocationId` | MCP audit entity |
| `AuditEntry` | `AuditId` | Consent/export/purge |

## Identity generation

- Prefer UUIDv7 (time-ordered) for `EventId`, `SessionId`, `ChunkId`, etc.
- `StoreOffset` is a database-monotonic bigint distinct from UUID ids.
- External keys (file paths, SHAs) are **not** primary keys; they are unique business keys on nodes.
