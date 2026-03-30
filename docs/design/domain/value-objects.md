# Value Objects

Value objects are immutable, equality-by-value, and validated on construction. Invalid values raise domain errors before persistence.

## Identifiers

| VO | Rules |
| --- | --- |
| `WorkspaceId` | UUIDv7 |
| `ActorId` | UUIDv7 |
| `DeviceId` | UUIDv7 |
| `EventId` | UUIDv7 |
| `SessionId` | UUIDv7 |
| `ChunkId` | UUIDv7 |
| `NodeId` / `EdgeId` | UUIDv7 |
| `CredentialId` | UUIDv7 |
| `ConflictId` | UUIDv7 |
| `StoreOffset` | `int >= 0` |

## Event envelope VOs

| VO | Rules |
| --- | --- |
| `EventType` | `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$` max 128 |
| `SchemaVersion` | `int >= 1` |
| `IdempotencyKey` | 8–200 chars; opaque to server |
| `SourceName` | enum-like string: `vscode`, `cursor`, `browser`, `desktop`, `api`, `sync`, `system`, `git-hook` |
| `CorrelationId` | 8–128 chars |
| `PayloadFingerprint` | hex sha256 of canonical JSON payload |

## Time and ranges

| VO | Rules |
| --- | --- |
| `Instant` | UTC timestamp with millisecond precision minimum |
| `TimeRange` | `start < end`; both UTC |
| `IdleTimeout` | duration 1m–24h; default 30m |
| `ReplayCursor` | opaque server cursor string |

## Policy / consent

| VO | Rules |
| --- | --- |
| `ConsentCategory` | `editor` \| `terminal` \| `git` \| `browser` \| `assistant` \| `build` |
| `RetentionClass` | see data-retention doc |
| `AlgorithmVersion` | string `v1`, `v2`, … |
| `RedactionProfile` | named profile id, e.g. `default-v1` |

## Memory / search

| VO | Rules |
| --- | --- |
| `EmbeddingModelId` | non-empty; includes provider + model name |
| `EmbeddingVector` | fixed dims matching model; finite floats |
| `SearchQuery` | 1–2000 chars query text + optional filters |
| `SearchFilters` | time_range, sources[], types[], session_id?, device_id? |

## Graph

| VO | Rules |
| --- | --- |
| `NodeType` | `file` \| `symbol` \| `commit` \| `pull_request` \| `session` \| `decision` \| `actor` \| `url` |
| `EdgeType` | `touched` \| `implements` \| `reviews` \| `caused_by` \| `references` \| `contains` |
| `NodeKey` | `(NodeType, external_key)` with normalized path/URL rules |

## Sync

| VO | Rules |
| --- | --- |
| `SyncCursor` | `(device_id, workspace_id, last_offset)` |
| `DeviceFingerprint` | stable hash from client; optional |

## Naming / display

| VO | Rules |
| --- | --- |
| `WorkspaceName` | trimmed; 1–120 chars |
| `DeviceLabel` | trimmed; 1–80 chars |

## Construction pattern (Python intent)

```python
@dataclass(frozen=True, slots=True)
class IdempotencyKey:
    value: str

    def __post_init__(self) -> None:
        if not (8 <= len(self.value) <= 200):
            raise DomainValidationError("idempotency key length out of range")
```

No setters; transformations return new instances.
