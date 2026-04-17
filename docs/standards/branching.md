# Branching Strategy

## Primary branches

| Branch | Role | Protection |
| --- | --- | --- |
| `main` | Integration; always releasable | PRs required; CI green |
| `release/x.y` | Stabilize a minor line; patches only | Maintainer-managed |

Feature work does not live permanently on long-running branches.

## Branch naming

```
<type>/<area>-<short-summary>
```

| Prefix | Use |
| --- | --- |
| `feat/` | Features |
| `fix/` | Bug fixes |
| `docs/` | Documentation |
| `refactor/` | Refactors |
| `chore/` | Tooling/hygiene |
| `perf/` | Performance |
| `test/` | Test-only |
| `ci/` | CI |

Examples: `feat/ingest-batch-endpoint`, `fix/api-pagination-cursor`, `docs/standards-phase4`

Rules:

- lowercase kebab-case
- no personal names as sole branch name
- keep short-lived (days to a couple of weeks)

## Workflow

1. Branch from latest `main`
2. Open PR early if design feedback is needed (draft OK)
3. Rebase onto `main` for clean local history **or** merge `main` in when shared
4. Squash or rebase merge per repository GitHub settings; preserve conventional commit message
5. Delete branch after merge

## Hotfixes

1. Branch from `release/x.y` or tag `vX.Y.Z`
2. PR into release branch
3. Tag patch release
4. Merge/cherry-pick back to `main`

## Forbidden practices

- Force-push to `main` or `release/*`
- Committing directly to `main` except emergency maintainer procedures documented in an incident note
- Long-lived feature branches without sync to `main` (>2 weeks without rebase/merge requires justification)

## Alignment with releases

See [release.md](release.md) and [RELEASE.md](../../RELEASE.md).
