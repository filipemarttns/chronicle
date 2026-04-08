# Event Flow Diagram

Steady-state path from capture to queryable memory.

```mermaid
flowchart LR
    subgraph Capture
        E1[Editor events]
        E2[Terminal events]
        E3[Git events]
        E4[Browser opt-in]
        E5[AI opt-in]
    end

    subgraph WritePath
        V[Validate + Auth + Consent]
        R[Redact]
        L[Append Event Log]
        O[Outbox]
    end

    subgraph Projectors
        S[Session projector]
        T[Timeline projector]
        M[Memory / embed projector]
        G[Graph projector]
        A[Analytics aggregator]
    end

    subgraph Query
        Q1[Replay API]
        Q2[Search API]
        Q3[Graph API]
        Q4[MCP tools]
    end

    E1 --> V
    E2 --> V
    E3 --> V
    E4 --> V
    E5 --> V
    V --> R --> L --> O
    O --> S
    O --> T
    O --> M
    O --> G
    O --> A
    S --> Q1
    T --> Q1
    M --> Q2
    M --> Q4
    G --> Q3
    G --> Q4
    A --> Q1
```

## Ordering guarantees

| Concern | Guarantee |
| --- | --- |
| Persist order per workspace | Append transaction order + `received_at` |
| Producer time | `occurred_at` retained; may be skewed |
| Projection order | By event store offset / monotonic id |
| Cross-device | Converges after sync; temporary divergence allowed |

## Backpressure

When embed or graph queues exceed configured depth, ingest continues by default (durability first). Operators may enable degrade modes that reject non-critical event types—documented in deployment runbooks.
