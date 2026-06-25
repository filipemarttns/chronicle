# Support

This document explains how to get help with Chronicle, what maintainers can reasonably provide, and how to file reports that lead to fast, accurate responses.

Chronicle is an open-source, self-hosted **Developer Memory Engine**. Support is community-driven. There is no guaranteed SLA unless a separate commercial agreement exists.

## 1. Before asking for help

1. Read the [README.md](README.md) Quick Start.
2. Confirm your issue is not already answered in [DEVELOPMENT.md](DEVELOPMENT.md) or [ARCHITECTURE.md](ARCHITECTURE.md).
3. Search [GitHub Issues](https://github.com/chronicle-dev/chronicle/issues) and [Discussions](https://github.com/chronicle-dev/chronicle/discussions).
4. Reproduce on the latest released version or current `main` when possible.
5. Redact secrets, tokens, private URLs, and personal file paths from all logs and screenshots.

## 2. Support channels

| Channel | Use for | Do not use for |
| --- | --- | --- |
| GitHub Discussions | How-to questions, design clarification, roadmap feedback | Vulnerability reports |
| GitHub Issues | Confirmed bugs, actionable feature requests | Vague troubleshooting without details |
| Pull requests | Fixes and improvements you are contributing | Drive-by “please implement X for me” without context |
| security@chronicle.dev | Security vulnerabilities | General product questions |
| conduct@chronicle.dev | Code of Conduct violations | Technical support |

Maintainers may convert Issues to Discussions (or vice versa) when the channel is wrong.

## 3. What maintainers support

Maintainers prioritize:

- Defects in released versions and `main`
- Security reports filed through the proper channel
- Documentation gaps that block installation or safe operation
- Contributions that follow [CONTRIBUTING.md](CONTRIBUTING.md)
- Clear regressions with reproductions

Maintainers do not guarantee:

- Custom architecture reviews for private deployments
- Hands-on debugging of proprietary environments
- Immediate answers outside voluntary contributor time
- Support for unmodified forks that diverge significantly from upstream
- Recovery of data lost due to operator misconfiguration without backups

## 4. Bug reports

A high-quality bug report includes:

1. **Summary** — what failed in one sentence
2. **Version** — git tag or commit SHA; container image digest if applicable
3. **Deployment** — Docker Compose, host-native, OS, architecture
4. **Steps to reproduce** — minimal and ordered
5. **Expected behavior**
6. **Actual behavior** — including error messages
7. **Logs** — redacted API/worker logs with correlation ids when available
8. **Impact** — ingest down, search wrong, timeline incomplete, etc.
9. **Workarounds** — if any

### Template

```markdown
### Summary


### Version


### Environment
- OS:
- Deploy method:
- Python/Node versions (if host-native):

### Steps to reproduce
1.
2.
3.

### Expected


### Actual


### Redacted logs / screenshots


### Additional context
```

Issues lacking reproduction details may be closed after a request for information goes unanswered.

## 5. Feature requests

Feature requests should explain:

- The problem you are solving (not only the preferred solution)
- How it fits [ROADMAP.md](ROADMAP.md) or why it should change the roadmap
- Privacy/consent implications if new capture or export behavior is involved
- Whether you are willing to contribute an implementation

Requests that primarily enable silent surveillance of developers without consent controls will be declined per project non-goals.

## 6. Operational incidents (self-hosted)

For production-like self-hosted deployments, collect:

- Projection lag / queue depth
- Disk usage for PostgreSQL
- Recent migrations applied
- Whether retention jobs ran
- Backup age and restore test status

Disaster recovery and capacity planning documents live under [`docs/deployment/`](docs/deployment/). Prefer restoring from a known-good backup over ad-hoc event store edits.

**Never** manually mutate the event log to “fix” production data without a documented recovery procedure—projections and embeddings depend on append-only semantics.

## 7. Privacy-sensitive support

Chronicle may contain highly sensitive engineering data. When seeking help:

- Prefer synthetic reproductions
- Minimize datasets attached to issues
- Strip Authorization headers, cookies, and tokens
- Avoid uploading full timeline exports publicly
- Use private maintainer contact only when necessary for security issues

Maintainers will not request more raw event data than required and will ask for redaction when submissions are oversharing.

## 8. Community expectations

- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- Prefer evidence over speculation
- Assume good faith
- Do not pressure maintainers for unpaid emergency support
- If you find an answer, document it back into Discussions or docs via PR

## 9. Commercial and consulting inquiries

If you need dedicated support, training, or custom integration work, contact the Lead Maintainer listed in [MAINTAINERS.md](MAINTAINERS.md). Commercial arrangements are separate from community governance and must not override [GOVERNANCE.md](GOVERNANCE.md) or the [MIT License](LICENSE).

## 10. Status of project maturity

Chronicle's documentation foundation and implementation milestones are described in [ROADMAP.md](ROADMAP.md). Early milestones may be incomplete; support answers will distinguish **documented intended behavior** from **not yet implemented**.

When something is missing, the correct outcome is often an issue labeled as a roadmap gap—not a bug.

## 11. Related documents

- [README.md](README.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [RELEASE.md](RELEASE.md)
- [MAINTAINERS.md](MAINTAINERS.md)

Early RC operators should pin image digests when publishing internal mirrors.

