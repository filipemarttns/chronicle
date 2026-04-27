# Release Strategy (Standards)

Operational detail lives in [RELEASE.md](../../RELEASE.md). This standard binds engineering practice to that policy.

## Versioning

Semantic Versioning 2.0.0. During `0.x`, breaking changes may ship in minors but require explicit changelog + migration notes.

Public interfaces: HTTP `/vN`, event schemas, documented env vars, MCP tools, extension settings keys.

## Cadence

| Kind | Trigger |
| --- | --- |
| Patch | Defects, security, doc-critical fixes |
| Minor | Milestone features on roadmap |
| Major | Breaking contract changes post-1.0 |
| RC / beta | Stabilization before minor/major |

`main` must remain releasable; cutting a release should not require heroic cleanup.

## Engineering gates before tag

1. CI green on release commit
2. Migrations upgrade from previous tag on clean Compose
3. OpenAPI export reviewed for unintended breaks
4. Changelog section complete
5. Security issues of critical severity addressed or explicitly deferred with advisory plan
6. Benchmark gates for minor/major per [performance.md](performance.md)

## Artifacts

- Git tag `vX.Y.Z`
- Container images digest-pinned in release notes when published
- Extension builds aligned to release train when in scope

## Rollback

Prefer forward fixes. Do not delete published tags. Mark broken releases in notes. Expand/contract DB migrations preferred over irreversible rewrites.

## Ownership

Only maintainers with release authority publish tags and official artifacts ([MAINTAINERS.md](../../MAINTAINERS.md)).
