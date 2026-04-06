# Component Diagram

C4 Level 3 — API and worker internals (logical components).

```mermaid
flowchart TB
    subgraph Inbound["Inbound adapters"]
        HTTP["HTTP Controllers"]
        MCP["MCP Tool Adapters"]
        AuthN["AuthN Middleware"]
        Redact["Redaction Pipeline"]
    end

    subgraph Application["Application services"]
        IngestSvc["IngestService"]
        SessionSvc["SessionService"]
        TimelineSvc["TimelineQueryService"]
        SearchSvc["SearchService"]
        GraphSvc["GraphQueryService"]
        SyncSvc["SyncService"]
        ConsentSvc["ConsentService"]
    end

    subgraph Domain["Domain"]
        SessionAgg["Session Aggregate"]
        Envelope["Event Envelope VOs"]
        Policies["Consent & Retention Policies"]
    end

    subgraph Outbound["Outbound adapters"]
        EventStore["EventStoreRepository"]
        Outbox["OutboxPublisher"]
        SessionProj["SessionProjector"]
        TimelineProj["TimelineProjector"]
        EmbedWorker["EmbeddingWorker"]
        GraphProj["GraphProjector"]
        VectorIdx["VectorIndexAdapter"]
    end

    HTTP --> AuthN --> Redact --> IngestSvc
    MCP --> AuthN
    IngestSvc --> Envelope
    IngestSvc --> EventStore
    IngestSvc --> Outbox
    IngestSvc --> Policies
    SessionSvc --> SessionAgg
    TimelineSvc --> TimelineProj
    SearchSvc --> VectorIdx
    GraphSvc --> GraphProj
    Outbox --> SessionProj
    Outbox --> TimelineProj
    Outbox --> EmbedWorker
    Outbox --> GraphProj
```

## Hexagonal mapping

| Port (example) | Adapter |
| --- | --- |
| `EventStorePort` | SQLAlchemy PostgreSQL repository |
| `ClockPort` | System UTC clock / test clock |
| `EmbeddingPort` | Local model runner |
| `SearchPort` | pgvector query adapter |
| `JobEnqueuePort` | Outbox + Celery |
| `SecretRedactorPort` | Regex/heuristic redactor |

Domain components do not import FastAPI, Celery, or SQLAlchemy.
