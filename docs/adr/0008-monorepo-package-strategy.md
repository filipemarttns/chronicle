# ADR-0008: Monorepo and Package Strategy

- Status: Accepted
- Date: 2026-01-22
- Deciders: Lead Maintainer
- Tags: repo, packaging

## Context

Event schemas, API contracts, extensions, and web clients change together. Polyrepos create version skew: an extension may emit events the API no longer accepts, or the web console may call endpoints removed in a patch.

## Decision

Keep Chronicle as a **monorepo** with clear packages:

- `apps/*` — runnable processes (api, worker, web, desktop, mcp)
- `packages/domain`, `packages/application`, `packages/adapters`, `packages/schemas`
- `extensions/*` — editor and browser clients
- `docs/*` — deep documentation

Shared event and API schemas live in `packages/schemas` and are the single source of truth for producers and consumers in-repo.

Python packaging uses workspace-style installs; JavaScript uses pnpm workspaces.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Polyrepo per app | Schema drift; painful atomic changes |
| Single undifferentiated tree | Unclear dependency direction; harder ownership |
| Publish every package to PyPI/npm from day one | Premature versioning overhead |

## Consequences

- CI must selectively test affected packages but periodically run full suites.
- CODEOWNERS map paths to maintainers.
- External integrators consume published OpenAPI/schemas once release channels mature.
- Clone size grows; mitigate with sparse docs images if needed later.

## References

- ADR-0003, ADR-0009
