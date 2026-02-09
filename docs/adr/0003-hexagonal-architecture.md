# ADR-0003: Hexagonal Architecture and Dependency Rule

- Status: Accepted
- Date: 2026-01-16
- Deciders: Lead Maintainer
- Tags: structure, python, maintainability

## Context

Chronicle integrates many adapters: FastAPI, SQLAlchemy, Celery, Redis, embedding runtimes, editor extensions, and MCP. If domain rules import these frameworks directly, tests become slow, substitutions become hard, and architectural erosion accelerates.

## Decision

Organize backend code as **hexagonal (ports and adapters)** with a strict dependency rule:

1. `domain` — entities, value objects, aggregates, domain events, domain services; no framework imports
2. `application` — use cases/services orchestrating ports
3. `adapters` — inbound (HTTP, MCP) and outbound (Postgres, Redis, embedders)

Ports are interfaces defined inward; adapters implement them outward.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Framework-centric layered app (models in ORM everywhere) | Domain becomes untestable and storage-shaped |
| Microservices per context from day one | Operational overhead unjustified before product-market fit of the engine |
| Plugin-only architecture without a domain core | Encourages duplicated invariants across extensions |

## Consequences

- Slightly more boilerplate (ports, DTOs at edges).
- Pytest can exercise domain logic without Postgres.
- New capture protocols do not require domain rewrites.
- PR review must reject domain imports of FastAPI/SQLAlchemy/Celery.

## References

- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- ADR-0008
