# Domain and Application Services

## Domain services

Pure or port-dependent logic that does not naturally belong on a single aggregate.

| Service | Responsibility |
| --- | --- |
| `SessionClusteringService` | Deterministic open/touch/close decisions (ADR-0011) |
| `PayloadCanonicalizer` | Canonical JSON for fingerprints |
| `SecretRedactionService` | Apply detectors (may wrap port) |
| `ConsentEvaluator` | Whether a telemetry type is allowed |
| `NodeKeyNormalizer` | Path/URL normalization for graph keys |
| `ChunkingService` | Split events/diffs into MemoryChunk candidates |

## Application services (use cases)

Orchestrate transactions, authz, and ports. Invoked by HTTP/MCP adapters.

### IngestService

```text
ingest(command: IngestEventCommand) -> IngestResult
ingest_batch(command: IngestBatchCommand) -> BatchResult
```

Steps: authz → consent → redact → validate schema → idempotency check → append+outbox → result.

### SessionProjectionService

Applies telemetry to Session aggregate via clustering rules; persists session; may append `domain.session.*`.

### TimelineQueryService

```text
replay(query: ReplayQuery) -> Page[TimelineItemDTO]
```

### SearchService

```text
search(query: SearchQuery, actor) -> SearchResponse
```

Embed query → vector search → hydrate citations → redact response.

### GraphQueryService

```text
neighbors(node_id, depth, actor) -> GraphNeighborhoodDTO
```

### SyncService

```text
push(batch, device) -> SyncPushResult
pull(cursor, device) -> SyncPullResult
```

### ConsentService

```text
get_policy(workspace_id) -> ConsentPolicyDTO
update_category(workspace_id, category, enabled, actor) -> None
```

### RetentionService

```text
purge(command: PurgeCommand) -> PurgeResult
```

Respects legal hold; cascades deletions; appends retention domain event.

### McpToolService

```text
invoke(tool, args, actor) -> ToolResult
```

Authz → execute query service → redact → audit.

### WorkspaceAdminService

Create/archive workspace, issue credentials, register devices.

## Command / DTO naming

- Commands: `IngestEventCommand`, `PurgeCommand`, …
- Results: `IngestResult`, `AppendResult`, …
- DTOs at adapter edge may differ from domain objects; mapping is explicit.

## Transactions

| Use case | Transaction scope |
| --- | --- |
| Ingest | Single UoW: event + outbox |
| Consent update | ConsentPolicy save + domain event append |
| Sync push | Per-event ingest UoW or batched UoW with same idempotency rules |
| Search | Read-only |

## Idempotency of application services

- Ingest: key-based
- Purge: purge request id
- Sync pull: cursor-based
- Embed worker: chunk_id + model_id unique upsert
