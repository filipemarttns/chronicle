# Deployment Diagram

Reference topologies from laptop to hardened single-site.

## Local development / single-node

```mermaid
flowchart TB
    subgraph Host["Operator Host"]
        subgraph Compose["Docker Compose Network"]
            API[api]
            W[worker]
            SCH[scheduler]
            WEB[web]
            PG[(postgres)]
            RD[(redis)]
        end
        EXT[Editor / Browser Extensions]
        DESK[Tauri Desktop]
    end

    EXT --> API
    DESK --> API
    WEB --> API
    API --> PG
    API --> RD
    W --> PG
    W --> RD
    SCH --> RD
```

## Hardened single-site

```mermaid
flowchart TB
    subgraph Edge
        LB[TLS Reverse Proxy]
    end

    subgraph AppTier
        API1[api]
        API2[api]
        W1[worker pool]
        W2[embed pool]
    end

    subgraph DataTier
        PGp[(Postgres primary)]
        PGr[(Postgres replica)]
        RD[(Redis)]
        BAK[Encrypted backups]
    end

    Clients[Clients] --> LB --> API1
    LB --> API2
    API1 --> PGp
    API2 --> PGp
    API1 --> RD
    W1 --> PGp
    W2 --> PGp
    W1 --> RD
    PGp --> PGr
    PGp --> BAK
```

## Deployment principles

1. API is horizontally scalable behind a load balancer.
2. Workers scale independently; embed workers may use GPU hosts.
3. Postgres primary is the write authority; replicas serve heavy read/search when configured.
4. Redis is not a durable system of record.
5. Backups encrypt event payloads at rest in backup storage.

See [../deployment/scaling.md](../deployment/scaling.md) and [../deployment/disaster-recovery.md](../deployment/disaster-recovery.md).
