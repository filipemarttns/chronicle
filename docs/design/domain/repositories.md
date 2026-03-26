# Repository Ports

Repositories abstract persistence. Defined as Protocol/ABC in `packages/domain` or `packages/application` (ports), implemented in `packages/adapters`.

## EventStore

```text
append(envelope: EventEnvelope, uow: UnitOfWork) -> AppendResult
get(event_id: EventId) -> EventEnvelope | None
get_by_idempotency(workspace_id, key) -> EventEnvelope | None
read_from(workspace_id, offset: StoreOffset, limit: int) -> list[EventEnvelope]
```

`AppendResult`: `{ event_id, store_offset, created: bool }`

## OutboxRepository

```text
enqueue(job: OutboxJob, uow: UnitOfWork) -> None
claim_batch(limit: int) -> list[OutboxJob]
mark_published(job_id) -> None
mark_failed(job_id, error: str) -> None
```

## WorkspaceRepository

```text
save(workspace: Workspace) -> None
get(workspace_id) -> Workspace | None
```

## DeviceRepository

```text
save(device: Device) -> None
get(device_id) -> Device | None
find_by_fingerprint(workspace_id, fingerprint) -> Device | None
```

## CredentialRepository

```text
save(credential: Credential) -> None
find_by_token_hash(hash) -> Credential | None
```

## ConsentPolicyRepository

```text
get(workspace_id) -> ConsentPolicy
save(policy: ConsentPolicy) -> None
```

## SessionRepository

```text
save(session: Session) -> None
get(session_id) -> Session | None
find_open(workspace_id, device_id) -> Session | None
list(workspace_id, time_range, limit, cursor) -> Page[SessionSummary]
```

## TimelineReadRepository

```text
list_replay(workspace_id, filters: ReplayQuery) -> Page[TimelineItem]
```

## MemoryChunkRepository

```text
save_chunks(chunks: list[MemoryChunk]) -> None
list_unembedded(workspace_id, model_id, limit) -> list[MemoryChunk]
```

## VectorIndex

```text
upsert(chunk_id, model_id, vector: EmbeddingVector) -> None
search(workspace_id, vector, filters, k) -> list[SearchHit]
delete_by_chunk_ids(chunk_ids) -> None
```

## GraphRepository

```text
upsert_node(node: GraphNode) -> None
upsert_edge(edge: GraphEdge, evidence: list[EventId]) -> None
neighbors(node_id, depth, limit) -> GraphNeighborhood
```

## AnalyticsRepository

```text
upsert_window(sample: MetricSample) -> None
summary(workspace_id, range) -> AnalyticsSummary
```

## SyncCursorRepository

```text
get(workspace_id, device_id) -> SyncState
save(state: SyncState) -> None
```

## ConflictRepository

```text
save(conflict: ConflictRecord) -> None
list_open(workspace_id) -> list[ConflictRecord]
```

## AuditRepository

```text
append(entry: AuditEntry) -> None
```

## UnitOfWork

```text
commit() -> None
rollback() -> None
```

Ingest must use one UnitOfWork spanning `EventStore.append` + `OutboxRepository.enqueue`.

## Implementation rules

1. Repositories do not emit domain events themselves; application services decide.
2. No SQL leaks into domain.
3. Pagination VOs are shared (`Page`, `Cursor`).
4. Integration tests cover adapters; domain tests use fakes.
