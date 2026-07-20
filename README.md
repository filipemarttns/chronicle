# Chronicle

[![CI](https://github.com/filipemarttns/chronicle/actions/workflows/ci.yml/badge.svg)](https://github.com/filipemarttns/chronicle/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-0.1%20RC-orange.svg)](CHANGELOG.md)

**Developer Memory Engine**

Chronicle records engineering activity and turns it into a searchable, replayable memory layer for individuals and teams.

> **Status:** early release candidate (`0.1.0-rc.1`). The local stack below runs today. Broader capture surfaces, knowledge graph, and production OIDC are on the [roadmap](ROADMAP.md)—not all README vision items are shipped yet.

Engineers lose institutional context when teammates leave, branches go cold, or decisions bury themselves in chat. Chronicle treats development activity as first-class data: capture it once, query it later, and reconstruct the reasoning behind a change.

---

## Vision

Software organizations accumulate code. They rarely accumulate *understanding*.

Chronicle closes that gap with a durable memory layer—preserving not only what changed, but *why* it changed, *how* it was explored, and which signals led to the decision.

The long-term goal is a local-first substrate for timeline replay, semantic search, historical debugging, developer analytics, and assistants grounded in real work history.

## Problem Statement

Modern development produces high-signal artifacts that are discarded or siloed:

| Signal | Typical fate |
| --- | --- |
| Editor navigation and edits | Ephemeral; lost when the buffer closes |
| Terminal command sequences | Scrollback that disappears overnight |
| Browser research trails | Opaque history, never linked to code |
| Git commits and pull requests | Stored, but detached from session context |
| Stack traces and build failures | Logged, then forgotten |
| AI assistant conversations | Locked inside vendor UIs |
| Architecture decisions | Scattered across docs, issues, and memory |

Without a unifying model, engineers re-derive context repeatedly. Chronicle treats every signal as an **event**, groups events into **sessions**, indexes them for **retrieval**, and exposes them through a **timeline** (and, later, a knowledge graph).

## What works today

| Area | Available now |
| --- | --- |
| API | Ingest, timeline replay, search, consent, sessions, analytics summary, sync push/pull |
| Auth | `dev` (open local) and `token` (hashed workspace credentials + bootstrap) |
| Persistence | In-memory store or PostgreSQL + Alembic; Compose uses pgvector |
| Search | Hashing embeddings (CI-safe) with hybrid scoring; ANN path when pgvector is present |
| Web console | Timeline replay and search against the API |
| Workers | Celery outbox drain |
| MCP helpers | Tool-shaped functions for search/timeline/session summary (prototype) |
| VS Code extension | Emits `editor.file.opened` over HTTP |

## Planned (see ROADMAP)

Terminal/git/PR/browser/AI capture depth, knowledge graph, OIDC, real embedding models, multi-device sync hardening, and a full desktop control plane.

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

See [ARCHITECTURE.md](ARCHITECTURE.md), [`docs/`](docs/README.md), and [`docs/design/`](docs/design/README.md).

## Technology Stack

| Area | Choices |
| --- | --- |
| Backend | Python 3.14, FastAPI, SQLAlchemy, Alembic, Celery |
| Data | PostgreSQL, pgvector, Redis |
| Frontend | Next.js, TypeScript |
| Desktop | Tauri (stub control plane) |
| Extensions | VS Code / Cursor, Chromium-compatible browser extension (early) |
| Infrastructure | Docker, Docker Compose, GitHub Actions |
| Testing | Pytest (primary); broader web/e2e suites planned |

## Installation

### Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.14+ (for local backend development)
- Node.js 22+ (for the web console)

### Clone

```bash
git clone https://github.com/filipemarttns/chronicle.git
cd chronicle
```

### Quick start (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

The root [`compose.yaml`](compose.yaml) includes [`deploy/docker/docker-compose.yml`](deploy/docker/docker-compose.yml). Local Compose defaults to `CHRONICLE_AUTH_MODE=dev` so the console can call the API without a bearer token.

Services:

| Service | URL |
| --- | --- |
| API | http://localhost:8000 |
| API docs (OpenAPI) | http://localhost:8000/docs |
| Web console | http://localhost:3000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

```bash
curl -s http://localhost:8000/health
```

Optional smoke (API must be running):

```bash
python scripts/smoke_api.py
```

### Local development without containers

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Quick Start

1. Start the stack with Docker Compose.
2. Open http://localhost:3000 — enter a workspace UUID and use Timeline / Search.
3. (Optional) Load the VS Code extension from `extensions/vscode` in development mode.
4. Ingest events via the API or extension; replay them on the timeline.

### Example: ingest a manual event

```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -d @scripts/fixtures/sample_event.json
```

With `CHRONICLE_AUTH_MODE=token`, issue a bearer via `POST /v1/auth/tokens` and `X-Chronicle-Bootstrap` (see [DEVELOPMENT.md](DEVELOPMENT.md)), then add `-H "Authorization: Bearer $CHRONICLE_API_TOKEN"`.

### Example: semantic search

```bash
curl -X POST http://localhost:8000/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "11111111-1111-1111-1111-111111111111",
    "query": "pagination bug in events list endpoint",
    "limit": 10
  }'
```

## Documentation

| Document | Description |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Local workflows |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [ROADMAP.md](ROADMAP.md) | Milestones |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |
| [`docs/`](docs/README.md) | ADRs, design, deployment |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

MIT — see [LICENSE](LICENSE).

## Citation

```bibtex
@software{chronicle2026,
  title        = {Chronicle: Developer Memory Engine},
  author       = {Martins, Filipe and Chronicle Contributors},
  year         = {2026},
  url          = {https://github.com/filipemarttns/chronicle},
  license      = {MIT}
}
```

Also see [`CITATION.cff`](CITATION.cff).
