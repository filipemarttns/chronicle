# Python Package Strategy

## Packages

| Package | Name (import) | Responsibility |
| --- | --- | --- |
| Domain | `chronicle_domain` | Aggregates, VOs, domain events, domain services, ports (protocols) |
| Application | `chronicle_application` | Use cases / application services, command DTOs |
| Adapters | `chronicle_adapters` | SQLAlchemy, Redis/Celery, redactor impl, embedders, HTTP mappers |
| Schemas | `chronicle_schemas` | JSON Schema assets; optional codegen helpers |
| API app | `chronicle_api` | FastAPI app wiring |
| Worker app | `chronicle_worker` | Celery app wiring |
| MCP app | `chronicle_mcp` | MCP server entry |

Exact distribution names may use hyphens on PyPI later (`chronicle-domain`); imports use underscores.

## Dependency rule

```text
chronicle_api / chronicle_worker / chronicle_mcp
        → chronicle_application → chronicle_domain
        → chronicle_adapters → chronicle_application/chronicle_domain
chronicle_adapters may import chronicle_schemas
chronicle_domain must NOT import adapters, FastAPI, SQLAlchemy, Celery
```

See [dependency-rule.md](dependency-rule.md).

## Module sketch (`chronicle_domain`)

```text
chronicle_domain/
  identity/
    workspace.py
    device.py
    consent.py
  capture/
    envelope.py
  session/
    session.py
    clustering.py
  memory/
    chunking.py
  graph/
    keys.py
  shared/
    ids.py
    time.py
    errors.py
  ports/
    event_store.py
    ...
```

## Typing and docs

- Python 3.14+
- Public types fully annotated
- Docstrings on public aggregates and services
- `slots=True` frozen dataclasses for VOs preferred

## Testing

| Package | Test location |
| --- | --- |
| domain | `packages/domain/tests` — no I/O |
| application | fakes for ports |
| adapters | integration against Compose Postgres/Redis |
| api | HTTPX tests |

## Tooling

- `uv` workspaces or editable installs via root `pyproject.toml`
- `ruff` + type checker in CI
- Alembic lives with adapters or `apps/api` migrations package — **normative:** `packages/adapters/chronicle_adapters/persistence/migrations`
