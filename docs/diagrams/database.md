# Database Diagram

Logical schema for the event store and primary read models. Physical names may include schema prefixes; this diagram is normative for relationships, not every index.

```mermaid
erDiagram
    WORKSPACE ||--o{ EVENT : contains
    WORKSPACE ||--o{ DEVICE : has
    WORKSPACE ||--o{ CONSENT_GRANT : governs
    ACTOR ||--o{ EVENT : produces
    DEVICE ||--o{ EVENT : originates
    EVENT ||--o| OUTBOX : dispatches
    EVENT ||--o{ TIMELINE_ITEM : projects
    SESSION ||--o{ TIMELINE_ITEM : groups
    EVENT ||--o{ MEMORY_CHUNK : derives
    MEMORY_CHUNK ||--|| EMBEDDING : vectorizes
    EVENT ||--o{ GRAPH_EVIDENCE : evidences
    GRAPH_NODE ||--o{ GRAPH_EDGE : from
    GRAPH_NODE ||--o{ GRAPH_EDGE : to
    GRAPH_EDGE ||--o{ GRAPH_EVIDENCE : cites
    WORKSPACE ||--o{ SYNC_CURSOR : tracks
    WORKSPACE ||--o{ CONFLICT_RECORD : reports

    WORKSPACE {
        uuid id PK
        string name
        jsonb settings
        timestamptz created_at
    }

    ACTOR {
        uuid id PK
        string principal_type
        string display_name
    }

    DEVICE {
        uuid id PK
        uuid workspace_id FK
        string label
        string public_key_thumbprint
    }

    CONSENT_GRANT {
        uuid id PK
        uuid workspace_id FK
        string category
        bool enabled
        timestamptz changed_at
    }

    EVENT {
        uuid id PK
        uuid workspace_id FK
        uuid actor_id FK
        uuid device_id FK
        string type
        int schema_version
        string idempotency_key
        timestamptz occurred_at
        timestamptz received_at
        jsonb payload
        jsonb redaction_meta
        bigint store_offset
    }

    OUTBOX {
        uuid id PK
        uuid event_id FK
        string job_type
        string status
        timestamptz available_at
    }

    SESSION {
        uuid id PK
        uuid workspace_id FK
        uuid device_id FK
        timestamptz started_at
        timestamptz ended_at
        string algorithm_version
    }

    TIMELINE_ITEM {
        uuid id PK
        uuid session_id FK
        uuid event_id FK
        timestamptz occurred_at
        string item_kind
    }

    MEMORY_CHUNK {
        uuid id PK
        uuid workspace_id FK
        string chunk_kind
        text content
        jsonb citations
    }

    EMBEDDING {
        uuid chunk_id PK
        vector embedding
        string model_id
        int dims
    }

    GRAPH_NODE {
        uuid id PK
        uuid workspace_id FK
        string node_type
        string external_key
        jsonb props
    }

    GRAPH_EDGE {
        uuid id PK
        uuid from_node_id FK
        uuid to_node_id FK
        string edge_type
        jsonb props
    }

    GRAPH_EVIDENCE {
        uuid edge_id FK
        uuid event_id FK
    }

    SYNC_CURSOR {
        uuid device_id FK
        uuid workspace_id FK
        bigint last_offset
    }

    CONFLICT_RECORD {
        uuid id PK
        uuid workspace_id FK
        string idempotency_key
        jsonb local_fingerprint
        jsonb remote_fingerprint
        timestamptz detected_at
    }
```

## Indexing notes

| Table | Critical indexes |
| --- | --- |
| EVENT | `(workspace_id, idempotency_key)` UNIQUE; `(workspace_id, store_offset)`; `(workspace_id, occurred_at)` |
| TIMELINE_ITEM | `(session_id, occurred_at)`; `(workspace_id, occurred_at)` via join/denorm |
| EMBEDDING | HNSW on `embedding` (ADR-0014) |
| GRAPH_EDGE | `(from_node_id, edge_type)`; `(to_node_id, edge_type)` |
| OUTBOX | `(status, available_at)` |

## Partitioning

Large deployments partition `EVENT` by time or hash of `workspace_id`. Projections may follow. See [../deployment/capacity-planning.md](../deployment/capacity-planning.md).
