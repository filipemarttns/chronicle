# Commit Conventions

Chronicle uses [Conventional Commits](https://www.conventionalcommits.org/). Full contributor-facing summary also lives in [CONTRIBUTING.md](../../CONTRIBUTING.md); this document is normative for tooling and review.

## Format

```
<type>(<optional scope>): <imperative summary>

<optional body>

<optional footer>
```

## Types

| Type | Use |
| --- | --- |
| `feat` | New user-visible capability or domain behavior |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Internal change without behavior change |
| `perf` | Performance improvement |
| `test` | Tests only |
| `build` | Build system or dependencies |
| `ci` | CI configuration |
| `chore` | Maintenance not covered elsewhere |
| `revert` | Revert prior commit |

## Scopes

Non-exhaustive: `memory`, `ingest`, `timeline`, `search`, `graph`, `sync`, `api`, `domain`, `db`, `worker`, `web`, `desktop`, `vscode`, `browser`, `mcp`, `security`, `docs`, `ci`, `standards`, `schemas`

## Subject rules

1. Imperative mood: `add`, `fix`, `reject` — not `added` / `fixes`
2. ≤ 72 characters preferred
3. No trailing period
4. No emoji
5. Describe why-impact when space allows; detail belongs in body

## Body rules

- Explain motivation and trade-offs for non-trivial changes
- Reference design docs/ADRs when invariants change
- Call out migration steps
- Do not paste secrets or real event payloads

## Footers

```
Fixes #123
Refs #456
BREAKING CHANGE: description
```

During `0.x`, `BREAKING CHANGE` still requires release-note callouts even if semver major stays 0.

## Examples

```
docs: add architecture overview

feat(memory): implement event ingestion pipeline

refactor(domain): extract aggregate root interfaces

fix(api): resolve pagination issue on event list endpoint

perf(search): optimize vector similarity queries

test(session): cover idle timeout clustering edge cases

ci: add path-filtered pytest workflow
```

## Atomicity

- One logical change per commit when practical
- Do not mix unrelated refactors with feature work
- Generated lockfile updates may accompany the dependency change that caused them

## Authorship

Commits should reflect the human author responsible for the change. Co-authored-by trailers are allowed when multiple contributors collaborate.
