# Release Process

This document defines how Chronicle versions are assigned, built, validated, tagged, and published. The goal is predictable releases that operators can trust with sensitive engineering data.

## 1. Versioning policy

Chronicle follows [Semantic Versioning 2.0.0](https://semver.org/):

Given a version `MAJOR.MINOR.PATCH`:

| Increment | When |
| --- | --- |
| **MAJOR** | Breaking changes to public HTTP APIs, event schema compatibility guarantees, or documented operator workflows |
| **MINOR** | Backward-compatible features, new event types that old consumers can ignore, new optional endpoints |
| **PATCH** | Backward-compatible bug fixes, security hardening, documentation that does not change behavior |

### Pre-release tags

| Tag | Meaning |
| --- | --- |
| `-alpha.N` | Unstable; APIs may change without notice |
| `-beta.N` | Feature-complete for the milestone; fixing defects |
| `-rc.N` | Release candidate; production-shaped validation |

Examples: `0.1.0-alpha.1`, `0.3.0-beta.2`, `1.0.0-rc.1`, `1.0.0`.

### 0.x phase

While the major version is `0`, minor bumps may include breaking changes when necessary, but maintainers must:

1. Call them out in the changelog
2. Provide migration notes
3. Prefer additive evolution whenever feasible

Stabilization toward `1.0.0` requires documented API and schema compatibility commitments.

## 2. What constitutes a public interface

Breaking-change review applies to:

- HTTP APIs under `/v1` (and later majors)
- Versioned event envelopes and registered event types
- Documented environment variables and config semantics
- Extension settings keys that are documented for operators
- MCP tool names and argument schemas once declared stable
- Database upgrade paths published for a release line

Internal packages, experimental flags, and undocumented endpoints may change with weaker guarantees but still require changelog notes when operators might notice.

## 3. Release cadence

| Cadence | Intent |
| --- | --- |
| Continuous | Merges to `main` remain releasable |
| Minor | Feature milestones per [ROADMAP.md](ROADMAP.md) |
| Patch | As needed for defects and security |
| Security out-of-band | Immediately when severity requires |

Chronicle does not promise a fixed calendar date for minors; it promises process quality when a release is cut.

## 4. Branching for releases

| Branch | Role |
| --- | --- |
| `main` | Integration; default for PRs |
| `release/x.y` | Stabilization for a minor line; receives fixes only |
| tags `vX.Y.Z` | Immutable release markers |

Hotfixes:

1. Branch from the affected release tag or `release/x.y`
2. Land fix with tests
3. Tag patch release
4. Merge or cherry-pick back to `main`

## 5. Release checklist

### A. Prepare

- [ ] Confirm milestone scope is complete or explicitly deferred
- [ ] Ensure CI is green on the release commit
- [ ] Review open critical/high security issues
- [ ] Update `CHANGELOG.md` (Keep a Changelog structure)
- [ ] Update version fields in packages/apps consistently
- [ ] Verify migrations upgrade cleanly from the previous release
- [ ] Verify Docker Compose path for fresh installs and upgrades
- [ ] Run benchmark smoke suite; attach summary for minor/major releases
- [ ] Confirm docs links and Quick Start commands

### B. Validate

- [ ] Unit + integration suites
- [ ] Playwright critical path (when UI is in scope)
- [ ] Extension load smoke test against the release API
- [ ] Dependency vulnerability scan reviewed
- [ ] Container images built reproducibly from the tagged commit

### C. Publish

- [ ] Create annotated git tag: `vX.Y.Z`
- [ ] Push tag to origin
- [ ] GitHub Release with changelog excerpt and migration notes
- [ ] Publish container images with the same version tags
- [ ] Publish extension artifacts to distribution channels when applicable
- [ ] Announce in GitHub Discussions for minor/major releases

### D. Post-release

- [ ] Monitor issues labeled `regression` for 72 hours
- [ ] File follow-up issues for known deferred items
- [ ] For security releases, publish advisory per [SECURITY.md](SECURITY.md)

## 6. Changelog requirements

Every released version must document:

- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security

Operator-facing migration steps belong in the release notes, not only in commit history.

## 7. Artifact naming

| Artifact | Tag pattern |
| --- | --- |
| Git tag | `v1.4.2` |
| Container image | `ghcr.io/filipemarttns/chronicle-api:<version>` (when published) |
| Compose bundle | referenced by git tag |
| VS Code extension | marketplace version aligned with semver policy |
| Desktop installers | `Chronicle-1.4.2-<platform>` |

Immutable digests should be recorded in the GitHub Release body when images are published.

## 8. Signing and provenance

As release automation matures:

- Tags are created by maintainers with release authority
- CI produces provenance attestations for container images where supported
- Checksums for desktop installers are published alongside binaries
- Extension packages follow store signing requirements

Until signing is fully automated, maintainers manually verify artifact hashes before announcement.

## 9. Rollback policy

If a release is severely defective:

1. Publish a patch that fixes forward when safe
2. If forward fix is not viable, document last known good tag and pin instructions
3. Mark the GitHub Release as broken with a clear banner in the notes
4. Never delete public tags that others may have deployed; supersede them

Database migrations that cannot roll back must be called out **before** operators upgrade. Prefer expand/contract patterns.

## 10. Security releases

- May omit feature freeze formalities
- Must not omit tests for the fix
- Coordinated disclosure timing follows [SECURITY.md](SECURITY.md)
- Credit reporters unless anonymity is requested

## 11. Who can release

Only maintainers listed in [MAINTAINERS.md](MAINTAINERS.md) with release permissions may push version tags and publish official artifacts. Contributors prepare release PRs; maintainers execute publication.

## 12. Release PR template

```markdown
## Version
- Target: vX.Y.Z

## Changes
- Link to changelog section

## Risk
- Migrations: yes/no
- API breaks: yes/no
- Event schema: compatible / additive / breaking

## Validation
- [ ] CI green
- [ ] Compose upgrade tested
- [ ] Benchmarks smoke (if minor/major)
- [ ] Security review for sensitive changes
```

## 13. Related documents

- [GOVERNANCE.md](GOVERNANCE.md) — release authority and escalation
- [SECURITY.md](SECURITY.md) — vulnerability handling
- [ROADMAP.md](ROADMAP.md) — milestone intent
- [DEVELOPMENT.md](DEVELOPMENT.md) — local validation before tagging
