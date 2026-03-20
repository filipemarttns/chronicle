# Phase 3 — System Design

This directory is the **implementation-facing design** for Chronicle: domain model, event catalog, repository and service contracts, OpenAPI v1, and package/monorepo layout.

Phase 1–2 documents remain authoritative for vision, ADRs, and operations. When code lands, it must match these contracts or update them in the same change set.

## Contents

| Document | Purpose |
| --- | --- |
| [domain/overview.md](domain/overview.md) | Domain model map by bounded context |
| [domain/aggregates.md](domain/aggregates.md) | Aggregate roots and invariants |
| [domain/entities.md](domain/entities.md) | Entities |
| [domain/value-objects.md](domain/value-objects.md) | Value objects |
| [domain/domain-events.md](domain/domain-events.md) | Domain events (write-side) |
| [domain/repositories.md](domain/repositories.md) | Repository ports |
| [domain/services.md](domain/services.md) | Domain and application services |
| [events/catalog.md](events/catalog.md) | Capture telemetry event definitions |
| [events/schemas.md](events/schemas.md) | JSON Schema conventions |
| [api/openapi-v1.yaml](api/openapi-v1.yaml) | OpenAPI 3.1 specification |
| [api/versioning.md](api/versioning.md) | Versioning strategy (design view) |
| [packages/monorepo.md](packages/monorepo.md) | Monorepo strategy |
| [packages/python.md](packages/python.md) | Python package layout |
| [packages/typescript.md](packages/typescript.md) | TypeScript / frontend package layout |
| [packages/dependency-rule.md](packages/dependency-rule.md) | Allowed dependency directions |

## Design freeze rules

1. Public HTTP paths and error codes change only via [api/versioning.md](api/versioning.md).
2. Event envelope fields change only via ADR + catalog update.
3. Aggregate invariants change only via ADR when semantic.
4. Package boundaries change only with maintainer review.
