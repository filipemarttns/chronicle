# Monorepo Strategy

## Decision

Chronicle is a **single monorepo** (ADR-0008) containing backend, workers, web, desktop, extensions, schemas, docs, and deploy assets.

## Goals

1. Atomic changes across event schema + API + extension
2. One CI entrypoint with path-filtered jobs
3. Shared glossary and design docs next to code
4. Clear package boundaries via dependency rules

## Top-level layout (normative target)

```text
chronicle/
  apps/
    api/
    worker/
    web/
    desktop/
    mcp/
  packages/
    domain/           # pure Python domain
    application/      # use cases
    adapters/         # infra adapters (may split later)
    schemas/          # JSON Schema + shared IDL
    ui/               # shared React primitives (optional)
    ts-client/        # generated/handwritten API client
  extensions/
    vscode/
    browser/
  docs/
  deploy/
    docker/
  tests/
    integration/
    e2e/
  scripts/
  .github/
  README.md
  ...
```

## Ownership

CODEOWNERS maps:

| Path | Owner area |
| --- | --- |
| `packages/domain/**` | Domain & Event Model |
| `apps/api/**` | Ingestion & API |
| `extensions/vscode/**` | Editor Extensions |
| `docs/adr/**` | Documentation + Lead |

## Change classification

| Change type | Required updates |
| --- | --- |
| New telemetry type | `packages/schemas`, catalog doc, extension emitter, projector if needed |
| New HTTP endpoint | OpenAPI, API app, tests, maybe ts-client |
| Invariant change | ADR + domain tests + this design tree |

## CI strategy

- Always: lint/typecheck for touched languages
- Path filters: run Python tests if `apps/**` or `packages/**` Python changes
- Nightly: full suite + benchmarks smoke
- Release: full suite + image build + OpenAPI export

## What does not belong in the monorepo

- Large binary datasets
- Real user event dumps
- Vendor secrets
- Machine-specific IDE state

## Escape hatch

If a package becomes a widely consumed standalone library, it may later publish from the monorepo via tagged releases without splitting git history. Polyrepo split requires an ADR.
