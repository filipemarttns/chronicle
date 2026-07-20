# Maintainers

This file lists active maintainers, their ownership areas, and how to reach the project for non-security matters.

Security vulnerabilities must be reported per [SECURITY.md](SECURITY.md), not via public mention of individual maintainers.

## Lead Maintainer

| Name | GitHub | Focus |
| --- | --- | --- |
| Filipe Martins | [@filipemarttns](https://github.com/filipemarttns) | Project stewardship, architecture coherence, releases |

## Area Maintainers

Ownership is modular so reviews land with people who understand the invariants of each subsystem.

| Area | Scope | Maintainer |
| --- | --- | --- |
| Domain & Event Model | Aggregates, domain events, schema versioning | Filipe Martins |
| Ingestion & API | FastAPI boundaries, authn hooks, OpenAPI | Filipe Martins |
| Persistence | PostgreSQL, Alembic, SQLAlchemy mappings, pgvector | Filipe Martins |
| Workers & Async | Celery, Redis, projection pipelines | Filipe Martins |
| Search & Memory | Embeddings, retrieval, indexing workers | Filipe Martins |
| Timeline & Replay | Session reconstruction, read models | Filipe Martins |
| Knowledge Graph | Graph projection and traversal APIs | Filipe Martins |
| Web Console | Next.js application | Filipe Martins |
| Desktop | Tauri shell and local control plane | Filipe Martins |
| Editor Extensions | VS Code / Cursor extension | Filipe Martins |
| Browser Extension | Opt-in research capture | Filipe Martins |
| MCP | Model Context Protocol server | Filipe Martins |
| Security | Threat response coordination, hardening defaults | Filipe Martins |
| CI / Release | GitHub Actions, release automation | Filipe Martins |
| Documentation | Architecture docs, ADRs, operator guides | Filipe Martins |

As the contributor base grows, area ownership will be split among additional maintainers without changing the meaning of these boundaries.

## Review expectations

Maintainers should:

- Respond to review requests in their areas within a reasonable window (goal: 5 business days)
- Enforce architectural boundaries described in [ARCHITECTURE.md](ARCHITECTURE.md)
- Require tests and documentation appropriate to the change
- Escalate cross-cutting or security-sensitive changes per [GOVERNANCE.md](GOVERNANCE.md)

## CODEOWNERS

When `.github/CODEOWNERS` is present, it is the machine-enforceable mapping of paths to maintainers. This file remains the human-readable source of role intent; keep both aligned.

## Emeritus Maintainers

Contributors who previously served as maintainers and have stepped down remain recognized here for project history.

| Name | Notes |
| --- | --- |
| — | No emeritus maintainers yet |

## Becoming a maintainer

See the nomination process in [GOVERNANCE.md](GOVERNANCE.md). Sustained contribution quality matters more than volume.

## Contact

| Topic | Channel |
| --- | --- |
| General questions | GitHub Discussions |
| Bugs and features | GitHub Issues |
| Security | GitHub Security Advisories / filipemarttns@gmail.com |
| Conduct | filipemarttns@gmail.com |
| Maintainer nominations | Private email to the Lead Maintainer |

## Affiliation disclaimer

Maintainer affiliations with employers are personal and do not imply that those employers endorse or support Chronicle unless explicitly stated in a sponsorship agreement.
