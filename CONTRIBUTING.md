# Contributing to Chronicle

Thank you for investing time in Chronicle. This document defines how to propose changes, what reviewers expect, and how to keep the repository coherent as it grows.

Participation in this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

| Contribution type | Expected process |
| --- | --- |
| Bug report | Open a GitHub issue with reproduction steps and environment details |
| Security vulnerability | Follow [SECURITY.md](SECURITY.md); do not open a public issue |
| Documentation fix | Pull request against `main` (or the active release branch if backporting) |
| Small code fix | Issue optional; pull request with tests |
| Feature or design change | Issue or discussion first; ADR if the change is architectural |
| Performance work | Issue with baseline measurements; PR with benchmark evidence |

## Before you start

1. Read [ARCHITECTURE.md](ARCHITECTURE.md), [DEVELOPMENT.md](DEVELOPMENT.md), and [docs/standards/](docs/standards/README.md).
2. Search issues, discussions, and ADRs for prior decisions.
3. Confirm the change aligns with [ROADMAP.md](ROADMAP.md) or justify a deliberate departure.
4. For changes that alter bounded contexts, event schemas, persistence, or public APIs, propose an ADR draft before implementation.

## Development setup

Follow [DEVELOPMENT.md](DEVELOPMENT.md) for toolchain installation, Docker Compose, migrations, and extension loading.

Minimum verification before requesting review:

```bash
# Backend
make lint
make typecheck
make test

# Frontend / extensions (from package roots)
pnpm lint
pnpm typecheck
pnpm test
```

Exact Make targets and package scripts are defined as the codebase lands; do not submit changes that weaken the verification bar established for the area you touch.

## Branching

| Branch | Purpose |
| --- | --- |
| `main` | Stable integration branch; must remain releasable |
| `release/x.y` | Release stabilization and patch backports |
| `feat/<area>-<summary>` | Feature work |
| `fix/<area>-<summary>` | Bug fixes |
| `docs/<summary>` | Documentation-only changes |
| `refactor/<area>-<summary>` | Structural improvements without behavior change |
| `chore/<summary>` | Tooling, CI, and repository hygiene |

Prefer short-lived branches. Rebase onto `main` before final review when history is local and not shared; otherwise merge `main` into your branch and resolve conflicts explicitly.

## Commit messages

Chronicle uses [Conventional Commits](https://www.conventionalcommits.org/). The normative rules are in [docs/standards/commits.md](docs/standards/commits.md). Summary:

```
<type>(<optional scope>): <imperative summary>

<optional body>

<optional footer>
```

### Types

| Type | Use when |
| --- | --- |
| `feat` | User-visible capability or new domain behavior |
| `fix` | Defect correction |
| `docs` | Documentation only |
| `refactor` | Internal restructuring without behavior change |
| `perf` | Performance improvement |
| `test` | Tests only |
| `build` | Build system or dependencies |
| `ci` | Continuous integration configuration |
| `chore` | Maintenance that does not fit other types |
| `revert` | Reverts a previous commit |

### Scopes (non-exhaustive)

`memory`, `ingest`, `timeline`, `search`, `graph`, `sync`, `api`, `domain`, `db`, `worker`, `web`, `desktop`, `vscode`, `browser`, `mcp`, `security`, `docs`, `ci`

### Examples

```
docs: add architecture overview

feat(memory): implement event ingestion pipeline

refactor(domain): extract aggregate root interfaces

fix(api): resolve pagination issue on event list endpoint

perf(search): optimize vector similarity queries
```

Rules:

- Use the imperative mood (“add”, not “added”).
- Limit the subject line to 72 characters when practical.
- Explain *why* in the body when the change is non-obvious.
- Reference issues with `Fixes #123` or `Refs #123` in the footer.
- Never commit secrets, credentials, or production event dumps.

## Pull requests

### Requirements

1. **Single purpose** — one concern per PR whenever feasible.
2. **Description** — problem, approach, alternatives considered, and risk.
3. **Tests** — unit coverage for domain logic; integration tests for API and persistence boundaries; e2e for user-critical paths when UI is involved.
4. **Documentation** — update user-facing docs, ADRs, and OpenAPI when behavior changes.
5. **Compatibility** — note any migration, deprecation, or breaking API impact.
6. **Security** — call out new trust boundaries, secrets handling, or data retention effects.

### Review criteria

Reviewers evaluate:

- Correctness against domain invariants
- Alignment with hexagonal boundaries (no infrastructure leaking into domain)
- Event schema compatibility and versioning
- Observability (structured logs, metrics, trace propagation)
- Performance impact on ingest and query paths
- Clarity of naming and documentation

Trivial documentation fixes may be merged by a maintainer with a single approval. Behavioral changes require at least one maintainer approval for the owned area. Cross-cutting architectural changes require consensus per [GOVERNANCE.md](GOVERNANCE.md).

### Checklist (include in PR body)

```markdown
## Summary
- 

## Motivation
- 

## Test plan
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated where boundaries change
- [ ] Manual verification steps documented
- [ ] Benchmarks attached for perf-sensitive changes

## Compatibility
- [ ] No breaking API change, or migration notes included
- [ ] Event schema version noted if applicable
- [ ] Docs / ADR updated if required
```

## Coding standards

### General

- Prefer clarity over cleverness.
- Keep functions and modules focused; extract when a unit acquires multiple reasons to change.
- Match existing style in the package you edit.
- Do not introduce new dependencies without justification and license review.

### Backend (Python)

- Python 3.14+, fully typed.
- Public functions and domain types require docstrings.
- Domain packages must not import FastAPI, SQLAlchemy engine details, or Celery APIs directly; depend on ports.
- Use explicit error types at domain and application boundaries.
- Prefer pure domain logic with deterministic tests.

### Frontend and extensions (TypeScript)

- Strict TypeScript; avoid `any` unless isolated and justified.
- Prefer composition over deep inheritance.
- Keep UI state predictable; document non-obvious side effects.
- Accessibility is part of completion criteria for interactive surfaces.

### Tests

| Layer | Expectation |
| --- | --- |
| Domain | Fast unit tests; no network or database |
| Application services | Unit or lightweight integration with fakes |
| Adapters | Integration tests against real Postgres/Redis in CI |
| UI | Component tests plus Playwright for critical flows |

Flaky tests are treated as defects. Fix or quarantine with an issue; do not ignore.

## Event schema changes

Events are the system of record. Changing them requires discipline:

1. Additive fields are preferred.
2. Renames and removals require a version bump and migration plan.
3. Producers and consumers must tolerate unknown fields.
4. Document the change in an ADR when the semantic meaning of an event type changes.

## Documentation contributions

Documentation is a first-class deliverable:

- Use professional technical English.
- Prefer precise terms from the project glossary (Event, Session, Timeline, Memory, Knowledge Graph, Replay, Ingestion).
- Do not use placeholder prose, marketing filler, or unexplained acronyms.
- Keep diagrams adjacent to the concepts they explain.
- Update the table of contents and cross-links when adding pages under `docs/`.

## Issue triage

Maintainers label issues for type, area, and priority. Contributors may suggest labels; maintainers own final classification.

If an issue is accepted but not scheduled, it remains open until a milestone is assigned or it is closed as out of scope with a rationale.

## Release participation

Release mechanics are defined in [RELEASE.md](RELEASE.md). Contributors should not cut releases unless asked by a maintainer. Patch nominations for stable branches are welcome via cherry-pick PRs.

## Community communication

| Channel | Use for |
| --- | --- |
| GitHub Issues | Bugs, concrete feature requests |
| GitHub Discussions | Design questions, proposals, Q&A |
| Pull request threads | Change-specific review |

Assume good faith. Prefer evidence—reproductions, profiles, schema diffs—over assertion.

## Legal

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE) and that you have the right to submit them.

Do not contribute code you are not authorized to share. Do not submit captured personal engineering data from private environments as fixtures unless it has been fully synthetic or scrubbed.

## Questions

If contributing process is unclear, open a Discussion or ask in an existing related issue. For security-sensitive questions, use the contact path in [SECURITY.md](SECURITY.md).
