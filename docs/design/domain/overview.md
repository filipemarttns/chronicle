# Domain Model Overview

Chronicle’s domain is organized by bounded contexts (see [bounded-contexts.md](../architecture/bounded-contexts.md)). This document maps **aggregates → entities → value objects → domain events → repositories → services**.

## Ubiquitous language (enforced)

| Term | Meaning in code and docs |
| --- | --- |
| Event | Immutable telemetry or domain fact in the event log |
| Envelope | Standard metadata around a payload |
| Session | Time-bounded unit of work for `(workspace, device)` |
| Timeline | Ordered replay projection |
| Memory | Searchable chunks + embeddings |
| Knowledge Graph | Rebuildable node/edge projection |
| Workspace | Isolation and policy boundary |
| Actor | Principal that produces or owns activity |
| Device | Capture origin identity |
| Consent | Per-category capture permission |

## Context → building blocks

| Context | Aggregate roots | Key VOs | Domain events | Primary repos |
| --- | --- | --- | --- | --- |
| Identity & Access | Workspace, Device, Credential | WorkspaceId, ActorId, DeviceId, ConsentCategory | WorkspaceCreated, DeviceRegistered, ConsentChanged, CredentialRotated | WorkspaceRepository, DeviceRepository, CredentialRepository |
| Capture & Ingestion | (transactional service; no long-lived aggregate beyond batch) | EventEnvelope, IdempotencyKey, EventType | EventAccepted, EventRejected | EventStore, OutboxRepository |
| Session | Session | SessionId, IdleTimeout, AlgorithmVersion | SessionStarted, SessionClosed, SessionMerged | SessionRepository |
| Timeline | — (read model) | ReplayCursor, TimeRange | TimelineProjected | TimelineReadRepository |
| Memory & Search | MemoryIndex (logical) | ChunkId, EmbeddingModelId, SearchQuery | MemoryChunksEmbedded, MemoryReindexed | MemoryChunkRepository, VectorIndex |
| Knowledge Graph | GraphSnapshot (logical rebuild unit) | NodeKey, EdgeType | GraphProjected | GraphRepository |
| Analytics | MetricWindow | MetricName, WindowSize | AnalyticsAggregated | AnalyticsRepository |
| Sync | SyncState | SyncCursor, PayloadFingerprint | SyncBatchApplied, SyncConflictDetected | SyncCursorRepository, ConflictRepository |
| Automation / MCP | — | ToolName, RedactionProfile | ToolInvocationRecorded | AuditRepository |

## Layering

```
adapters (HTTP, SQL, Celery, MCP)
        ↓
application services (use cases)
        ↓
domain (aggregates, VOs, domain services, domain events)
        ↑
repository ports (interfaces defined beside domain/application)
```

Implementation packages: [packages/python.md](packages/python.md).
