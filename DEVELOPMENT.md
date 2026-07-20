# Development Guide

This guide explains how to work on Chronicle locally with a setup that mirrors the reference architecture: API, workers, PostgreSQL with pgvector, Redis, and the web console.

Implementation packages land progressively per [ROADMAP.md](ROADMAP.md). Commands below describe the **intended** developer experience; when a target is not yet present in the tree, prefer the Docker Compose path and track gaps with issues.

## 1. Goals of the local environment

- Reproduce ingest → event store → projection → query flows
- Keep domain tests fast and infrastructure-free
- Make migrations intentional and reviewable
- Support extension development against a local API
- Fail loudly when consent, auth, or schema validation is misconfigured

## 2. Prerequisites

| Tool | Version | Purpose |
| --- | --- | --- |
| Git | 2.42+ | Version control |
| Docker | 24+ | Reference runtime |
| Docker Compose | v2 | Multi-service orchestration |
| Python | 3.14+ | API, workers, domain packages |
| uv or pipx + pip | current | Python environment management |
| Node.js | 22+ | Web, extensions |
| pnpm | 9+ | JavaScript workspace installs |
| Rust + Cargo | stable | Tauri desktop |
| just or make | optional | Task runners (repository will standardize on one) |

### System libraries

- pgvector-enabled PostgreSQL is provided via Docker images; host installs are optional.
- Tauri depends on platform-specific WebView libraries; follow Tauri prerequisites for Windows, macOS, or Linux.

## 3. Repository orientation

Target layout (see [ARCHITECTURE.md](ARCHITECTURE.md) for rationale):

```
apps/           Runnable services (api, worker, web, desktop, mcp)
packages/       Shared libraries (domain, application, adapters, schemas)
extensions/     VS Code/Cursor and browser extensions
docs/           Deep documentation (ADRs, diagrams, security, deployment)
deploy/docker/  Compose files and container build contexts
tests/          Cross-cutting integration and e2e harnesses
scripts/        Developer and CI helpers
```

Dependency rule: `packages/domain` must not import frameworks or drivers.

## 4. First-time setup

```bash
git clone https://github.com/filipemarttns/chronicle.git
cd chronicle
cp .env.example .env
```

Edit `.env` for local secrets. Never commit `.env`.

### Start infrastructure and services

```bash
docker compose up --build
```

Root [`compose.yaml`](compose.yaml) includes `deploy/docker/docker-compose.yml`. Local stacks default to `CHRONICLE_AUTH_MODE=dev`.

Typical local ports:

| Service | Port |
| --- | --- |
| API | 8000 |
| Web | 3000 |
| Postgres | 5432 |
| Redis | 6379 |

Health check:

```bash
curl -s http://localhost:8000/health
```

### Host-native API (optional)

When Python packages are available:

```bash
# example workflow — exact entrypoints ship with the API package
uv sync
uv run alembic upgrade head
uv run uvicorn apps.api.main:app --reload --port 8000
uv run celery -A apps.worker.celery_app worker -l INFO
```

Run web:

```bash
pnpm install
pnpm --filter @chronicle/web dev
```

## 5. Configuration

Configuration follows Twelve-Factor principles: environment variables, not committed machine-specific files.

Common variables (names illustrative; see `.env.example` when published):

| Variable | Purpose |
| --- | --- |
| `CHRONICLE_ENV` | `local` \| `test` \| `production` |
| `CHRONICLE_STORE` | `memory` \| `postgres` |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CHRONICLE_AUTH_MODE` | `dev` (open) \| `token` (Bearer) |
| `CHRONICLE_BOOTSTRAP_TOKEN` | One-time bootstrap secret to issue API tokens |
| `CHRONICLE_AUTH_PEPPER` | Pepper mixed into stored token hashes |
| `EMBEDDING_PROVIDER` | `hashing` (default, CI-safe) |
| `CHRONICLE_EMBEDDING_DIMS` | Vector size (default `384`) |
| `LOG_LEVEL` | `INFO` by default |

### Auth (token mode)

With `CHRONICLE_AUTH_MODE=token`, protected routes require `Authorization: Bearer <token>`.

Issue a workspace credential using the bootstrap header:

```bash
curl -s -X POST http://localhost:8000/v1/auth/tokens \
  -H "Content-Type: application/json" \
  -H "X-Chronicle-Bootstrap: $CHRONICLE_BOOTSTRAP_TOKEN" \
  -d '{"workspace_id":"<uuid>","actor_id":"<uuid>","label":"local"}'
```

Use the returned `token` on subsequent calls. Tokens are stored hashed (SHA-256 + pepper); the raw value is shown once.

Development auth must never be copied into production deployments.

## 6. Database and migrations

- Schema changes go through Alembic only.
- Migrations must be reversible when practical; destructive migrations require a rollback note in the PR.
- Review migration SQL in PRs affecting production-shaped environments.
- After pulling `main`:

```bash
uv run alembic upgrade head
```

Creating a migration:

```bash
uv run alembic revision --autogenerate -m "add_session_projection_tables"
```

Autogenerate is a starting point, not an authority—edit for correctness.

## 7. Working with events

### Schema discipline

1. Define or update the versioned schema in `packages/schemas`.
2. Add compatibility tests (old consumers tolerate new optional fields).
3. Update OpenAPI examples.
4. If semantics change, draft an ADR.

### Manual ingest

```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Authorization: Bearer $CHRONICLE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @./scripts/fixtures/sample_event.json
```

Prefer fixtures that are fully synthetic. Do not commit real command histories, URLs with tokens, or private source paths.

## 8. Testing strategy

| Layer | Tooling | Rules |
| --- | --- | --- |
| Domain unit | Pytest | No I/O; deterministic clocks injected |
| Application | Pytest + fakes | Ports mocked; assert orchestration |
| API integration | Pytest + HTTPX | Real Postgres/Redis in Compose CI profiles |
| Workers | Pytest | Idempotency under retry |
| Web unit | Vitest | Components and client logic |
| E2E | Playwright | Critical console flows |
| Extension | Vitest / VS Code test host | Activation and event emission |

Commands (intended):

```bash
make test
make test-integration
pnpm test
pnpm test:e2e
```

Coverage expectations will be enforced per package as CI matures. New domain logic should ship with tests in the same PR.

## 9. Static analysis and typing

| Area | Tools |
| --- | --- |
| Python types | `ty` / `mypy` / `pyright` as standardized in CI |
| Python lint | `ruff` |
| TS types | `tsc --noEmit` |
| TS lint | `eslint` |
| Security scan | dependency auditors in CI |
| Format | `ruff format`, Prettier |

Do not disable type errors to land features. Fix the types or narrow the design.

## 10. Extension development

### VS Code / Cursor

1. Start local API.
2. Open `extensions/vscode` in the editor.
3. Launch the Extension Development Host.
4. Point the extension settings at `http://localhost:8000` and your dev token.
5. Verify events appear via timeline or API list endpoints.

### Browser extension

1. Load the unpacked extension from `extensions/browser`.
2. Enable opt-in capture only on test profiles.
3. Confirm redaction behavior for URLs containing credentials.

## 11. Desktop development

```bash
pnpm --filter @chronicle/desktop tauri dev
```

Desktop code should treat the API as a remote boundary even when colocated, to preserve sync and auth assumptions.

## 12. Debugging projections

When timeline or search results look wrong:

1. Confirm the event exists in the event store.
2. Check worker logs for projection errors.
3. Inspect projection offset / lag metrics.
4. Rebuild the affected read model from a known offset in development only.
5. File a bug with event ids and projector versions—never with unredacted personal payloads.

## 13. Benchmarks

Performance-sensitive changes should include before/after numbers:

```bash
make bench
```

Publish methodology under `docs/benchmarks/` when adding new suites. Do not claim improvements without measurement.

## 14. Git workflow for contributors

Follow [CONTRIBUTING.md](CONTRIBUTING.md):

- Branch from `main`
- Conventional Commits
- Rebase or merge latest `main` before review
- Keep PRs focused

Suggested local hooks (optional until enforced):

- lint-staged formatters
- commit message linting
- secret scanning pre-push

## 15. Documentation while coding

Update docs in the same PR when you:

- Change API behavior
- Add environment variables
- Alter event schemas
- Change Docker topology
- Introduce operational runbooks

Architecture-significant work needs an ADR draft before or with the implementation PR per [GOVERNANCE.md](GOVERNANCE.md).

## 16. Privacy hygiene for developers

- Use synthetic fixtures.
- Scrub screenshots before posting to issues.
- Do not share `.env` contents.
- Prefer local embeddings and local models when experimenting with Memory features.
- Treat captured browser and AI data as sensitive even in development.

## 17. Troubleshooting

| Symptom | Checks |
| --- | --- |
| API cannot connect to DB | `DATABASE_URL`, Compose network, migration state |
| Events accepted but no timeline | Worker running? Redis reachable? Projector errors? |
| Extension not emitting | Consent toggles, auth token, API base URL |
| Search empty | Embedding worker lag, model download, vector migration |
| Flaky tests | Shared clock, unordered event assumptions, leaked Redis keys |

## 18. Getting help

- [SUPPORT.md](SUPPORT.md) for channels
- [ARCHITECTURE.md](ARCHITECTURE.md) for design intent
- GitHub Discussions for “how should I implement X?”

If the local guide drifts from scripts in the repo, trust executable scripts and open a docs PR.

The in-memory API profile is suitable for extension development before Postgres adapters land.

