# Hexagonal Ports Catalog

| Port | Direction | Responsibility |
| --- | --- | --- |
| `EventStorePort` | out | Append and read events by offset/id |
| `OutboxPort` | out | Enqueue durable jobs |
| `SessionRepositoryPort` | out | Persist session aggregate state if used on write side |
| `TimelineQueryPort` | out | Read timeline items |
| `EmbeddingPort` | out | Embed text/chunks |
| `VectorSearchPort` | out | ANN + hybrid queries |
| `GraphQueryPort` | out | Neighbor/path queries |
| `ClockPort` | out | UTC timestamps |
| `IdGeneratorPort` | out | UUIDs / ULID |
| `SecretRedactorPort` | out | Redact sensitive strings |
| `ConsentPolicyPort` | out | Evaluate category permission |
| `UnitOfWorkPort` | out | Transaction boundary |
| `AuditPort` | out | Write audit records |
| `HttpIngestAdapter` | in | FastAPI routes |
| `MCPAdapter` | in | Tool handlers |

New infrastructure technology requires a new adapter, not domain changes—unless invariants themselves change (then ADR).
