# Architecture

This document is the canonical high-level architecture for Chronicle, the **Developer Memory Engine**. It defines terminology, bounded contexts, runtime topology, consistency rules, and the rationale behind major structural choices.

Detailed diagrams, ADRs, threat models, and capacity plans live under [`docs/`](docs/README.md). When an ADR conflicts with this overview, the ADR wins for its scoped decision; this document must then be updated.

## 1. Purpose of the architecture

Chronicle must:

1. Ingest high-volume, heterogeneous engineering events with low loss and clear consent boundaries.
2. Persist an append-only history that remains interpretable years later.
3. Project that history into timelines, search indexes, graphs, and analytics.
4. Expose query and replay interfaces to humans, desktop/editor clients, and MCP-compatible assistants.
5. Remain operable as a local-first, self-hosted system with optional multi-device sync.

The architecture optimizes for **durability of meaning**, not merely storage of logs.

## 2. Glossary

| Term | Definition |
| --- | --- |
| **Event** | Immutable fact about something that occurred (e.g., file opened, command run, commit created). System of record unit. |
| **Event envelope** | Standard metadata wrapping every event: id, type, schema version, occurred_at, received_at, source, actor, workspace, device, payload, causation/correlation ids. |
| **Session** | Coherent unit of engineering work derived from events (time-bounded, workspace-aware). |
| **Timeline** | Ordered view of events and session markers suitable for replay. |
| **Memory** | Searchable representation of history, including embeddings and summaries. |
| **Knowledge Graph** | Network of entities (files, symbols, PRs, people, decisions) and relationships projected from events. |
| **Replay** | Reconstruction of a historical window with enough fidelity to answer “what happened and why.” |
| **Ingestion** | Path by which capture clients submit events to the system. |
| **Projection** | Asynchronous derivation of a read model from the event log. |
| **Capture surface** | Editor extension, browser extension, desktop agent, hooks, or API client that produces events. |

## 3. Architectural styles and why they are used

| Style | Application in Chronicle | Justification |
| --- | --- | --- |
| **Hexagonal Architecture** | Domain at the center; adapters for HTTP, DB, queues, embeddings | Keeps capture protocols and storage engines replaceable without rewriting invariants |
| **Domain-Driven Design** | Bounded contexts, aggregates, ubiquitous language | Prevents a “big ball of mud” around events, sessions, and search |
| **Event Sourcing** | Append-only event log as source of truth | Years of activity must remain reconstructable; mutable rows destroy history |
| **CQRS** | Separate write (ingest) and read (timeline/search/graph) models | Ingest needs durability and idempotency; queries need denormalized speed |
| **Repository Pattern** | Ports for aggregates and event stores | Tests domain logic without PostgreSQL; clarifies persistence boundaries |
| **Service Layer** | Application services orchestrate use cases | Keeps controllers thin and domain pure |
| **Clean Architecture principles** | Dependency rule toward domain | Avoids FastAPI/SQLAlchemy leaking into core policies |
| **Twelve-Factor App** | Config via env, backing services as attached resources, disposability | Enables Docker Compose parity with production-shaped deployments |

Chronicle does **not** use event sourcing as a fashion statement. Mutating a “current session” table as the only record would make timeline replay and historical debugging unverifiable.

## 4. System context

```
                 ┌──────────────────────┐
                 │  Developer / Operator │
                 └──────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌────────────────┐  ┌─────────────────┐
│ VS Code/Cursor│  │ Browser Ext    │  │ Tauri Desktop   │
│ Extension     │  │ (opt-in)       │  │ Control Plane   │
└───────┬───────┘  └────────┬───────┘  └────────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │ HTTPS / local IPC
                            ▼
                 ┌──────────────────────┐
                 │   Chronicle System   │
                 │  API · Workers · DB  │
                 └──────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌────────────────┐  ┌─────────────────┐
│ Next.js       │  │ MCP Clients    │  │ Git Host APIs   │
│ Web Console   │  │ (assistants)   │  │ (PR metadata)   │
└───────────────┘  └────────────────┘  └─────────────────┘
```

External actors never write projections directly. All durable facts enter through the ingestion boundary as events (or as commands that atomically append events).

## 5. Bounded contexts

| Context | Responsibility | Core aggregates |
| --- | --- | --- |
| **Identity & Access** | Actors, devices, tokens, workspaces, consent grants | Workspace, Device, Credential |
| **Capture & Ingestion** | Validate, authenticate, idempotently accept events | IngestBatch, EventEnvelope (write side) |
| **Session** | Cluster events into sessions; manage lifecycle | Session |
| **Timeline** | Ordered replay views and reconstruction queries | TimelineView (read model owned here) |
| **Memory & Search** | Chunking, embeddings, semantic/hybrid retrieval | MemoryIndex, SearchQuery |
| **Knowledge Graph** | Entity/relationship projection and traversal | GraphSnapshot, GraphNode, GraphEdge |
| **Analytics** | Aggregated productivity and workflow metrics | MetricWindow |
| **Sync** | Multi-device replication and conflict reporting | SyncCursor, ConflictRecord |
| **Automation / MCP** | Tool surface for assistants with redaction policy | ToolInvocation (audited) |

Context boundaries are package boundaries. Cross-context collaboration happens via domain events and application services—not via reaching into another context's tables.

## 6. Aggregate roots and invariants (initial set)

### Session

- A session has a stable id, workspace id, device id, start time, and optional end time.
- Events may be assigned to at most one open session per device/workspace policy.
- Closing a session is irreversible in the write model; corrections append compensating events.

### Event log (store)

- Events are immutable after append.
- Duplicate ingest keys do not create duplicate events (idempotency).
- `occurred_at` is producer time; `received_at` is server time; both are retained.
- Unknown event types may be stored as opaque payloads if schema policy allows, but versioned types are preferred.

### MemoryIndex

- Embeddings reference immutable event ids or chunk ids derived from them.
- Re-embedding produces new vectors without deleting historical provenance links unless retention requires it.

### Knowledge Graph

- Graph nodes/edges are projections; rebuilding from the event log must be possible.
- Edges carry evidence pointers (event ids) for explainability.

## 7. Domain events (representative)

Write-side domain events (not identical one-to-one with capture telemetry types) include:

| Domain event | Meaning |
| --- | --- |
| `EventAccepted` | Ingest persisted an event envelope |
| `SessionStarted` | Session aggregate opened |
| `SessionClosed` | Session aggregate closed |
| `SessionMerged` | Correction: sessions combined under policy |
| `TimelineProjected` | Read model advanced to an event offset |
| `MemoryChunksEmbedded` | Vectors written for a chunk set |
| `GraphProjected` | Graph projection advanced |
| `ConsentGranted` / `ConsentRevoked` | Capture category permission changed |
| `SyncBatchApplied` | Remote events merged |
| `RetentionPurged` | Data removed per policy |

Capture telemetry types (examples): `editor.file.opened`, `editor.file.edited`, `terminal.command.executed`, `git.commit.created`, `browser.page.visited`, `build.failed`, `assistant.interaction.recorded`.

Telemetry types are versioned strings. Domain events are the language of aggregates.

## 8. CQRS and data flow

```
Capture clients
      │
      ▼
 Ingest API ──► Event Store (PostgreSQL) ──► Outbox / Redis streams
                      │                              │
                      │                              ▼
                      │                     Celery workers
                      │                     ├─ Session projector
                      │                     ├─ Timeline projector
                      │                     ├─ Embedding worker
                      │                     ├─ Graph projector
                      │                     └─ Analytics aggregator
                      │
                      ▼
              Query APIs / MCP / UI  ◄── Read models (SQL, pgvector, graph tables)
```

**Write path priorities:** validation, authn/authz, idempotency, append durability, ack.

**Read path priorities:** latency, relevance, explainability (citations to event ids), consent-aware filtering.

Workers are idempotent. Replaying projections from an earlier offset must converge to the same read model for deterministic projectors.

## 9. Runtime containers

| Container | Role | Tech |
| --- | --- | --- |
| `api` | HTTP/JSON ingest and query | FastAPI, Uvicorn |
| `worker` | Async projections and embeddings | Celery |
| `scheduler` | Periodic backfills, retention jobs | Celery beat or equivalent |
| `postgres` | Event store + read models + vectors | PostgreSQL + pgvector |
| `redis` | Broker, cache, rate limit counters | Redis |
| `web` | Operator console | Next.js |
| `desktop` | Local shell (distributed separately) | Tauri |
| `mcp` | MCP server process (may colocated with api) | Python |

Docker Compose is the reference local topology. Production may split read replicas and worker pools without changing domain boundaries.

## 10. Persistence design

### Event store

- Append-only tables partitioned by time or workspace as scale requires.
- Unique constraint on ingest idempotency keys.
- Payload stored as JSONB with schema version column.
- Optional compression for cold partitions in later milestones.

### Read models

- Timeline tables indexed by `(workspace_id, occurred_at)`.
- Session tables with open/closed status and summary fields.
- Embedding tables with pgvector indexes (HNSW or IVFFlat chosen via ADR).
- Graph node/edge tables with evidence arrays.

### Migrations

Alembic owns schema evolution. Expanding event payload fields must remain backward compatible per versioning policy; destructive changes require dual-write or rebuild plans.

## 11. API surface (logical)

Versioned under `/v1`:

| Area | Examples |
| --- | --- |
| Events | `POST /v1/events`, `POST /v1/events:batch`, `GET /v1/events/{id}` |
| Sessions | `GET /v1/sessions`, `GET /v1/sessions/{id}` |
| Timeline | `GET /v1/timelines/replay` |
| Search | `POST /v1/search` |
| Graph | `GET /v1/graph/nodes/{id}/neighbors` |
| Analytics | `GET /v1/analytics/summary` |
| Sync | `POST /v1/sync/push`, `POST /v1/sync/pull` |
| Admin | health, readiness, retention policy endpoints |

Breaking changes require a new major version or explicitly versioned routes. See [RELEASE.md](RELEASE.md).

OpenAPI is generated from FastAPI and treated as a reviewable artifact.

## 12. Security architecture (summary)

- Authentication required outside explicitly local unauthenticated profiles.
- Consent grants gate capture categories before clients emit sensitive event types.
- Redaction hooks strip secrets from command lines and headers at ingest when detectors match.
- Exports and MCP tool responses apply scope and redaction policies.
- Retention jobs delete events and dependent projections for targeted scopes.

Full threat modeling belongs in `docs/security/`.

## 13. Observability

- Structured JSON logs with correlation ids from ingest through workers.
- Metrics: ingest rate, ack latency, queue depth, embed lag, search p95, projection lag.
- Tracing across API and workers where Celery instrumentation permits.
- Audit events for auth, consent changes, exports, and purges.

## 14. Failure modes and consistency

| Failure | Expected behavior |
| --- | --- |
| API crash after append, before ack | Client retries; idempotency prevents duplicates |
| Worker crash mid-projection | Restart resumes from offset; projector idempotency required |
| Redis broker outage | Ingest can still append if configured to defer enqueue; degraded mode documented |
| Partial embed failure | Chunk marked failed; retry without blocking ingest |
| Clock skew from clients | Prefer `occurred_at` with bounds checks; store `received_at` for ordering ties |

Chronicle chooses **durability of the event log** over perfect real-time projection freshness. Projection lag is monitored, not denied.

## 15. Monorepo layout (target)

```
chronicle/
  apps/
    api/                 # FastAPI application
    worker/              # Celery workers
    web/                 # Next.js console
    desktop/             # Tauri application
    mcp/                 # MCP server entrypoint
  packages/
    domain/              # Pure domain model
    application/         # Use cases / services
    adapters/            # Infrastructure adapters
    schemas/             # Shared event and API schemas
    ui/                  # Shared web UI primitives (if needed)
  extensions/
    vscode/
    browser/
  docs/
    adr/
    architecture/
    api/
    security/
    deployment/
    benchmarks/
    diagrams/
  deploy/
    docker/
  tests/
  scripts/
```

Exact package names may evolve, but the dependency rule does not: `domain` never imports adapters.

## 16. Quality attributes and targets

| Attribute | Target direction |
| --- | --- |
| Ingest throughput | Thousands of events/s on a single node with batching |
| Search latency | Sub-200 ms p95 for typical developer corpora at design point |
| Replay latency | Sub-second for hour-scale sessions via projections |
| Durability | No acknowledged event lost across planned restarts |
| Privacy | Opt-in for browser and AI; redaction on by default for known secret patterns |
| Rebuildability | Read models reconstructible from the event log |

Benchmarks and capacity planning will be published under `docs/benchmarks/` and `docs/deployment/`.

## 17. Explicit trade-offs

1. **Event sourcing complexity vs. auditability** — Accepted; rebuildability is a product requirement.
2. **Projection lag vs. synchronous indexing** — Prefer async workers so ingest stays fast.
3. **Local embeddings vs. hosted model APIs** — Prefer local/operator-controlled by default for privacy.
4. **Monorepo vs. polyrepo** — Prefer monorepo for atomic schema/API/extension changes.
5. **Strict schema vs. open payloads** — Prefer versioned schemas with controlled extensibility.

## 18. Evolution rules

1. Do not bypass the event log for durable facts.
2. Do not couple capture clients to read-model tables.
3. Do not add cross-context foreign key entanglements that prevent independent projection rebuilds.
4. Record material decisions as ADRs.
5. Update this document in the same change set when topology or invariants change.

## Related documents

- [README.md](README.md) — product overview
- [ROADMAP.md](ROADMAP.md) — milestone sequencing
- [DEVELOPMENT.md](DEVELOPMENT.md) — implementing against this architecture
- [SECURITY.md](SECURITY.md) — vulnerability reporting and security principles
- [GOVERNANCE.md](GOVERNANCE.md) — how architectural consensus is reached
