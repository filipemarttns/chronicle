# Dependency Rule

Hard constraints for the monorepo. Violations fail review (and eventually CI import-linters).

## Allowed

| From | To |
| --- | --- |
| apps/api | application, adapters, schemas, domain |
| apps/worker | application, adapters, schemas, domain |
| apps/mcp | application, adapters, domain |
| application | domain, ports defined with domain |
| adapters | domain, application (for interfaces only), schemas, drivers |
| domain | stdlib + typing only (no frameworks) |
| web/extension | ts-client, event-types, ui |

## Forbidden

| From | To | Why |
| --- | --- | --- |
| domain | fastapi, sqlalchemy, celery, redis, httpx | Keeps core pure |
| domain | adapters | Dependency inversion |
| schemas | apps | Schemas stay leaf-ish |
| vscode extension | sqlalchemy / Python | Wrong runtime |
| web | worker internals | Must use HTTP API |

## Import linters (intended)

- Python: `import-linter` contracts in CI
- TypeScript: ESLint `no-restricted-imports`

## Exception process

Temporary exceptions require:

1. Issue link
2. Expiration date
3. Maintainer approval

No permanent silent exceptions.
