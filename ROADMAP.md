# Roadmap

This roadmap describes Chronicle's product and technical direction. Dates are indicative and shift based on contributor capacity, security priorities, and feedback from early operators.

Chronicle ships in milestones. Each milestone must leave `main` releasable: documented, tested, and operable via Docker Compose.

## Principles guiding prioritization

1. **Correct capture before clever features** — incomplete or untrustworthy events undermine every higher layer.
2. **Local-first privacy** — capabilities that expand data leaving the operator's boundary require explicit consent and documentation.
3. **Event schema stability** — breaking the log is more expensive than delaying a UI feature.
4. **Replay fidelity** — timeline reconstruction quality is a primary product metric.
5. **Measurable performance** — ingest, embed, and search targets are enforced with benchmarks.

## Status legend

| Status | Meaning |
| --- | --- |
| Completed | Shipped and supported |
| In progress | Active development on `main` or a feature branch |
| Planned | Committed intent for the near horizon |
| Exploratory | Research; may be deferred or redesigned |

As of the documentation foundation phase, implementation milestones below are **Planned** unless noted.

---

## Milestone 0 — Repository foundation

**Theme:** Establish the project as a durable open-source system.

- Project charter, vision, and problem statement
- Governance, security policy, and contribution standards
- Architecture overview and terminology glossary
- Development and release processes
- Licensing and citation metadata

**Exit criteria:** Phase 1 root documents complete; contributors can understand scope without reading source.

---

## Milestone 1 — Event model and ingestion

**Theme:** Make engineering activity a reliable, append-only dataset.

### Domain

- Bounded contexts for Capture, Session, Timeline, and Identity
- Aggregate roots and domain events for session lifecycle
- Canonical event envelope (type, time, source, actor, workspace, payload, schema version)
- Idempotency and deduplication semantics

### Platform

- PostgreSQL event store schema via Alembic
- FastAPI ingest endpoints with authentication hooks
- Redis-backed rate limiting and job enqueue
- Celery worker skeleton for async projection

### Quality

- Contract tests for event schemas
- Integration tests for ingest durability
- OpenAPI for `/v1/events`

**Exit criteria:** A developer can ingest validated events and read them back in order with stable IDs.

---

## Milestone 2 — Timeline and session reconstruction

**Theme:** Turn raw events into coherent engineering sessions.

- Session aggregation rules (idle gaps, workspace switches, device boundaries)
- Timeline read models optimized for ordered playback
- Reconstruction API for time ranges and session IDs
- Basic web console timeline view
- Correlation of git commits with active sessions

**Exit criteria:** A one-hour coding session can be replayed with acceptable latency against the published benchmark targets.

---

## Milestone 3 — Memory, embeddings, and search

**Theme:** Make history queryable in natural language and by structure.

- Chunking strategy for events, diffs, and documents
- Local embedding pipeline (pgvector)
- Semantic search API with filters (time, source, workspace, event type)
- Hybrid retrieval (metadata predicates + vector similarity)
- Indexing workers with backfill and re-embed procedures

**Exit criteria:** Semantic queries return relevant results over a seeded corpus with documented p95 latency.

---

## Milestone 4 — Knowledge graph and analytics

**Theme:** Connect entities and quantify engineering patterns.

- Graph projection from events (files, symbols, PRs, decisions, people)
- Traversal APIs for neighborhood and path queries
- Developer analytics: focus blocks, context switches, review load
- ADR and decision linkage into the graph
- Export interfaces for offline analysis

**Exit criteria:** Operators can answer “what related to this file change?” without manual log archaeology.

---

## Milestone 5 — Capture surface completeness

**Theme:** Meet developers where work happens.

- VS Code / Cursor extension: editor, diagnostics, and terminal hooks
- Browser extension: opt-in research trail capture
- Git hooks / integrations for commits and PR metadata
- Tauri desktop shell for timeline and local control plane
- Consent UX and per-category toggles

**Exit criteria:** A self-hosted user can capture a full day of work across editor and git with explicit consent boundaries.

---

## Milestone 6 — MCP and AI memory interfaces

**Theme:** Expose Chronicle as memory infrastructure for assistants.

- Model Context Protocol server exposing search, timeline, and graph tools
- Guardrails for redaction and scope before tool responses leave the host
- Promptable memory summaries for sessions and incidents
- Foundation APIs for personalized assistant grounding (“AI clone” substrate)

**Exit criteria:** An MCP-compatible client can retrieve grounded context from a local Chronicle instance.

---

## Milestone 7 — Synchronization and multi-device

**Theme:** One developer's memory across machines.

- Device identity and workspace mapping
- Conflict-aware sync protocol for append-only events
- Offline capture with later reconciliation
- Conflict reports for non-commutative projections

**Exit criteria:** Two devices converge on a consistent event history under documented conflict rules.

---

## Milestone 8 — Hardening and production operations

**Theme:** Operate Chronicle as serious infrastructure.

- Threat model updates and security scanning in CI
- Backup, restore, and disaster recovery runbooks
- Retention policies and deletion cascades
- Observability defaults (metrics, traces, structured logs)
- Capacity planning guides and published benchmarks
- Horizontal scaling patterns for workers and read replicas

**Exit criteria:** A release candidate suitable for early production self-hosting with documented operational limits.

---

## Near-term release themes (next 6 months)

| Month focus | Outcomes |
| --- | --- |
| Month 1 | Repository setup, documentation, architecture |
| Month 2 | Core domain, database schemas, migrations |
| Month 3 | Backend APIs for ingest, session, and timeline |
| Month 4 | Frontend console and desktop foundations |
| Month 5 | Extensions and search engine |
| Month 6 | Optimization, CI/CD, documentation polish, release candidate |

This cadence matches the project's staged delivery plan and may compress or expand without changing milestone order.

## Explicit non-goals (current horizon)

The following are intentionally out of scope until foundational milestones are stable:

- Hosted multi-tenant SaaS as the default offering
- Silent capture without consent controls
- Training proprietary foundation models on user event data inside the open-source default path
- Replacing Git, issue trackers, or observability vendors
- Guaranteeing perfect productivity scoring as a managerial surveillance product

Chronicle is a **developer memory engine**, not an employee monitoring suite. Features that primarily serve surveillance without developer agency will be rejected.

## Proposal process

Roadmap changes that alter milestones, non-goals, or privacy posture require:

1. A GitHub Discussion or issue with motivation and trade-offs
2. Maintainer review per [GOVERNANCE.md](GOVERNANCE.md)
3. An ADR when the change is architectural
4. An update to this document in the same change set

## Feedback

Prioritization improves with real operator feedback: capture gaps, replay fidelity issues, search quality reports, and performance profiles. Open an issue with measurements whenever possible.
