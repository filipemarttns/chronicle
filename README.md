# Chronicle

**Developer Memory Engine**

Chronicle records engineering activity across editors, terminals, browsers, version control, and AI assistants, then transforms years of work into a searchable and replayable knowledge graph.

Engineers lose institutional context every time a teammate leaves, a branch goes cold, or a decision is buried in chat history. Chronicle treats development activity as first-class data: capture it once, query it forever, and reconstruct the reasoning behind every change.

---

## Vision

Software organizations accumulate code. They rarely accumulate *understanding*.

Chronicle exists to close that gap. It builds a durable memory layer for individual developers and engineering teams—one that preserves not only what changed, but *why* it changed, *how* it was explored, and *which* signals led to the final decision.

The long-term goal is a local-first memory substrate that can power timeline replay, semantic search, historical debugging, developer analytics, and eventually personalized AI assistants grounded in a developer's actual work history.

## Problem Statement

Modern development produces a continuous stream of high-signal artifacts that are discarded or siloed:

| Signal | Typical fate |
| --- | --- |
| Editor navigation and edits | Ephemeral; lost when the buffer closes |
| Terminal command sequences | Scrollback that disappears overnight |
| Browser research trails | Opaque history, never linked to code |
| Git commits and pull requests | Stored, but detached from session context |
| Stack traces and build failures | Logged, then forgotten |
| AI assistant conversations | Locked inside vendor UIs |
| Architecture decisions | Scattered across docs, issues, and memory |

Without a unifying model, engineers re-derive context repeatedly. Onboarding takes months. Incident response depends on tribal knowledge. AI tools hallucinate because they lack access to the real history of a codebase.

Chronicle addresses this by treating every engineering signal as an **event**, grouping events into **sessions**, indexing them for **semantic retrieval**, and exposing them through a **timeline** and **knowledge graph**.

## Features

### Capture

- **Editor activity** — VS Code and Cursor file opens, edits, selections, diagnostics, and extension events
- **Terminal commands** — shell invocations, exit codes, working directories, and duration
- **Git history** — commits, branches, merges, and authorship correlated with active sessions
- **Pull requests** — review threads, CI status, and merge outcomes
- **Browser history** — opt-in capture of research pages linked to active work
- **AI interactions** — assistant prompts and responses when integrations are enabled
- **Build and runtime signals** — compiler output, test results, and stack traces
- **Architecture decisions** — ADR ingestion and decision timeline linkage

### Memory and retrieval

- **Timeline replay** — reconstruct an engineering session second-by-second
- **Semantic search** — local embeddings over events, files, and decisions via pgvector
- **Knowledge graph** — entities (files, symbols, PRs, people, decisions) and their relationships
- **Session reconstruction** — cluster activity into coherent work units
- **Historical debugging** — ask “what was I doing when this broke?” and get a grounded answer
- **Developer analytics** — focus time, context switches, review load, and productivity metrics

### Platform

- **Event sourcing** — append-only event log as the system of record
- **CQRS** — separate write and read models optimized for ingestion and query
- **Local-first embeddings** — vectors computed and stored under operator control
- **Multi-device sync** — merge sessions across machines with conflict-aware replication
- **MCP support** — expose Chronicle memory to Model Context Protocol clients
- **AI clone foundation** — structured memory suitable for training or grounding personal assistants

## Architecture Overview

Chronicle follows **Hexagonal Architecture** and **Domain-Driven Design**, with **Event Sourcing** and **CQRS** as primary persistence and query strategies.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Capture Surface                                  │
│  VS Code Ext │ Cursor Ext │ Browser Ext │ Tauri Desktop │ Git Hooks     │
└───────────────┬────────────┴──────┬───────┴──────┬───────┴───────────────┘

                ▼                   ▼              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      Ingestion Boundary (FastAPI)                        │
│         Auth │ Validation │ Idempotency │ Rate limits │ Schemas          │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         Domain Core                                      │
│   Aggregates: Session · Timeline · MemoryIndex · KnowledgeGraph · Sync   │
│   Ports: EventStore · EmbeddingPort · SearchPort · GraphPort · Clock     │
└───────────────┬───────────────────┬──────────────────┬───────────────────┘
                │                   │                  │
                ▼                   ▼                  ▼
┌───────────────────┐  ┌────────────────────┐  ┌───────────────────────────┐
│  PostgreSQL       │  │  Redis             │  │  Celery Workers           │
│  + pgvector       │  │  Streams / Cache   │  │  Embed · Index · Sync     │
│  Event store      │  │  Job broker        │  │  Graph projection         │
└───────────────────┘  └────────────────────┘  └───────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      Query / Experience Layer                            │
│     Next.js Console │ Desktop Timeline │ Search API │ MCP Server         │
└──────────────────────────────────────────────────────────────────────────┘
```

| Layer | Responsibility | Primary technology |
| --- | --- | --- |
| Capture | Collect opt-in signals from developer tools | VS Code / Cursor extensions, browser extension, Tauri |
| API | Authenticate, validate, and accept events | FastAPI, Pydantic |
| Domain | Enforce invariants over sessions, timelines, and memory | Python domain packages |
| Persistence | Append events; project read models | PostgreSQL, Alembic, SQLAlchemy |
| Async processing | Embeddings, indexing, graph updates, sync | Celery, Redis |
| Experience | Timeline UI, search, analytics, MCP | Next.js, Tauri |

For the full design, see [ARCHITECTURE.md](ARCHITECTURE.md), the [`docs/`](docs/README.md) tree, and the Phase 3 implementation contract under [`docs/design/`](docs/design/README.md).

## Technology Stack

| Area | Choices |
| --- | --- |
| Backend | Python 3.14, FastAPI, SQLAlchemy, Alembic, Celery |
| Data | PostgreSQL, pgvector, Redis |
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Desktop | Tauri |
| Extensions | VS Code / Cursor, Chromium-compatible browser extension |
| Infrastructure | Docker, Docker Compose, GitHub Actions |
| Testing | Pytest, Playwright, Vitest |

## Installation

### Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.14+ (for local backend development)
- Node.js 22+ and pnpm 9+ (for web, desktop, and extensions)
- Rust toolchain (for Tauri desktop builds)

### Clone

```bash
git clone https://github.com/chronicle-dev/chronicle.git
cd chronicle
```

### Quick start (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

Services start on:

| Service | URL |
| --- | --- |
| API | http://localhost:8000 |
| API docs (OpenAPI) | http://localhost:8000/docs |
| Web console | http://localhost:3000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

Verify health:

```bash
curl -s http://localhost:8000/health | jq
```

### Local development without containers

See [DEVELOPMENT.md](DEVELOPMENT.md) for host-native workflows, database migrations, worker processes, and extension loading.

## Quick Start

1. Start the stack with Docker Compose as shown above.
2. Open the web console at http://localhost:3000 and complete first-run setup.
3. Install the VS Code / Cursor extension from the `extensions/vscode` package (development build) or from the marketplace release channel when published.
4. Enable capture categories you consent to (editor, terminal, git; browser and AI are opt-in).
5. Work normally for a few minutes, then open **Timeline** to replay the session.
6. Use **Search** to query natural-language questions such as “where did we change auth middleware last week?”

### Example: ingest a manual event

```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Authorization: Bearer $CHRONICLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "editor.file.opened",
    "occurred_at": "2026-03-12T14:22:01Z",
    "source": "vscode",
    "payload": {
      "path": "services/memory/src/indexer.py",
      "language": "python",
      "workspace_id": "ws_01HZX..."
    }
  }'
```

### Example: semantic search

```bash
curl -X POST http://localhost:8000/v1/search \
  -H "Authorization: Bearer $CHRONICLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pagination bug in events list endpoint",
    "limit": 10,
    "filters": { "time_range": "30d" }
  }'
```

## Documentation

| Document | Description |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, bounded contexts, and data flow |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Local setup, workflows, and tooling |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose changes and pass review |
| [ROADMAP.md](ROADMAP.md) | Near-term and long-term product direction |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and security posture |
| [GOVERNANCE.md](GOVERNANCE.md) | Decision-making and maintainer roles |
| [RELEASE.md](RELEASE.md) | Versioning, tagging, and release cadence |
| [SUPPORT.md](SUPPORT.md) | Where to ask questions and report issues |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community behavioral standards |
| [MAINTAINERS.md](MAINTAINERS.md) | Active maintainers and ownership areas |

Extended technical documentation lives under [`docs/`](docs/README.md): ADRs, threat models, diagrams, benchmarks, API contracts, and deployment guides.

## Benchmarks

Chronicle publishes reproducible benchmarks for ingestion throughput, search latency, and timeline reconstruction. Summary targets for a single-node development profile:

| Workload | Target | Notes |
| --- | --- | --- |
| Event ingest (sync API) | ≥ 5,000 events/s | Batched writes, idempotent keys |
| Embedding throughput | ≥ 200 chunks/s | Local model, CPU baseline |
| Semantic search p95 | ≤ 120 ms | Top-10 over 1M vectors |
| Timeline reconstruct (1h session) | ≤ 250 ms | Pre-projected read model |
| Knowledge graph hop (2-depth) | ≤ 80 ms | Indexed adjacency |

Methodology and machine profiles will be published under `docs/benchmarks/`. Numbers above are design targets used for capacity planning; measured results ship with each release candidate.

## Roadmap

High-level themes:

1. **Foundation** — event model, ingestion, storage, and authentication
2. **Memory** — embeddings, search, and session reconstruction
3. **Experience** — timeline UI, desktop shell, and editor extensions
4. **Intelligence** — MCP server, historical debugging assistants, analytics
5. **Scale** — multi-device sync, multi-tenant hardening, federation

Details: [ROADMAP.md](ROADMAP.md).

## Contributing

Contributions are welcome from engineers who care about developer tooling, information retrieval, and durable systems design.

Before opening a pull request:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [docs/standards/](docs/standards/README.md).
2. Search existing issues and discussions for duplicates.
3. Open an issue for design-impacting changes before large implementations.
4. Follow the repository's commit, testing, and documentation standards.

## License

Chronicle is released under the [MIT License](LICENSE).

## Security

Do not file security vulnerabilities as public GitHub issues.

Report them according to [SECURITY.md](SECURITY.md). Sensitive engineering data captured by Chronicle must remain under the operator's control; the default deployment model is local-first and self-hosted.

## Governance

Chronicle is stewarded by the maintainers listed in [MAINTAINERS.md](MAINTAINERS.md), under the policies defined in [GOVERNANCE.md](GOVERNANCE.md).

Significant technical decisions are recorded as Architecture Decision Records (ADRs) and require maintainer review.

## Citation

If you use Chronicle in academic work, benchmarking studies, or published evaluations, please cite:

```bibtex
@software{chronicle_developer_memory_engine,
  title        = {Chronicle: A Developer Memory Engine},
  author       = {Martins, Filipe and Chronicle Contributors},
  year         = {2026},
  url          = {https://github.com/chronicle-dev/chronicle},
  license      = {MIT}
}
```

## Maintainers

See [MAINTAINERS.md](MAINTAINERS.md) for ownership areas and contact paths.

Primary steward: **Filipe Martins**.

---

Chronicle records the work. You keep the understanding.

