# Architecture Decision Records

ADRs capture material technical decisions for Chronicle. Each record is numbered, dated, and status-tagged. Accepted ADRs are not edited in place for meaning; a superseding ADR references the prior number.

## Format

```
# ADR-NNNN: Title

- Status: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
- Date: YYYY-MM-DD
- Deciders: names or roles
- Tags: domain, storage, api, security, ...
```

Sections: Context, Decision, Alternatives Considered, Consequences, References.

## Index

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-event-sourcing-as-system-of-record.md) | Event sourcing as system of record | Accepted |
| [0002](0002-cqrs-read-model-separation.md) | CQRS read-model separation | Accepted |
| [0003](0003-hexagonal-architecture.md) | Hexagonal architecture and dependency rule | Accepted |
| [0004](0004-postgresql-event-store.md) | PostgreSQL as event store | Accepted |
| [0005](0005-pgvector-for-embeddings.md) | pgvector for local embeddings | Accepted |
| [0006](0006-redis-celery-async-workers.md) | Redis and Celery for async workers | Accepted |
| [0007](0007-fastapi-public-api.md) | FastAPI as public HTTP boundary | Accepted |
| [0008](0008-monorepo-package-strategy.md) | Monorepo and package strategy | Accepted |
| [0009](0009-event-envelope-versioning.md) | Event envelope and schema versioning | Accepted |
| [0010](0010-idempotent-ingestion.md) | Idempotent ingestion semantics | Accepted |
| [0011](0011-session-reconstruction-rules.md) | Session reconstruction rules | Accepted |
| [0012](0012-consent-scoped-capture.md) | Consent-scoped capture | Accepted |
| [0013](0013-local-first-deployment.md) | Local-first deployment default | Accepted |
| [0014](0014-hnsw-vector-index.md) | HNSW as default vector index | Accepted |
| [0015](0015-outbox-projection-dispatch.md) | Transactional outbox for projection dispatch | Accepted |
| [0016](0016-api-versioning-strategy.md) | API versioning strategy | Accepted |
| [0017](0017-mcp-tool-surface.md) | MCP tool surface and redaction | Accepted |
| [0018](0018-multi-device-sync-protocol.md) | Multi-device sync protocol | Accepted |
| [0019](0019-knowledge-graph-as-projection.md) | Knowledge graph as rebuildable projection | Accepted |
| [0020](0020-observability-standards.md) | Observability standards | Accepted |
| [0021](0021-secret-redaction-at-ingest.md) | Secret redaction at ingest | Accepted |
| [0022](0022-tauri-desktop-shell.md) | Tauri for desktop control plane | Accepted |

## Process

1. Draft ADR while the decision is still reversible.
2. Link the PR or Discussion.
3. Require maintainer review per [GOVERNANCE.md](../../GOVERNANCE.md).
4. Set status to Accepted when merged.
5. Update [ARCHITECTURE.md](../../ARCHITECTURE.md) if invariants or topology change.
