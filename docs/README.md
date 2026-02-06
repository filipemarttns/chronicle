# Chronicle Documentation

Technical documentation for Chronicle, the Developer Memory Engine.

Root-level documents ([README.md](../README.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [DEVELOPMENT.md](../DEVELOPMENT.md), and related policies) remain the entry points for contributors and operators. This tree deepens those topics with diagrams, ADRs, API contracts, security analysis, and operational runbooks.

## Contents

| Directory | Purpose |
| --- | --- |
| [architecture/](architecture/) | Bounded contexts, CQRS/ES mechanics, data model, hexagonal ports |
| [design/](design/) | Phase 3 system design: domain model, event catalog, OpenAPI, packages |
| [standards/](standards/) | Naming, commits, branching, testing, security, performance, and related norms |
| [adr/](adr/) | Architecture Decision Records (numbered, immutable once accepted) |
| [diagrams/](diagrams/) | C4-style and operational diagrams (Mermaid) |
| [api/](api/) | HTTP/MCP API conventions, versioning, error model |
| [security/](security/) | Threat model, retention, redaction, trust boundaries |
| [deployment/](deployment/) | Scaling, capacity planning, disaster recovery |
| [benchmarks/](benchmarks/) | Methodology, workloads, design targets |
| [roadmap/](roadmap/) | Milestone detail beyond [ROADMAP.md](../ROADMAP.md) |

## Reading order

1. [../ARCHITECTURE.md](../ARCHITECTURE.md) — system overview and glossary
2. [architecture/bounded-contexts.md](architecture/bounded-contexts.md) — domain seams
3. [design/README.md](design/README.md) — aggregates, APIs, packages (implementation contract)
4. [standards/README.md](standards/README.md) — engineering norms for contributors
5. [adr/README.md](adr/README.md) — decisions and trade-offs
6. [diagrams/system-context.md](diagrams/system-context.md) — visual topology
7. [security/threat-model.md](security/threat-model.md) — adversarial view
8. [deployment/capacity-planning.md](deployment/capacity-planning.md) — operate at scale
9. [api/overview.md](api/overview.md) — integrate clients

## Conventions

- Professional technical English
- Glossary terms from [ARCHITECTURE.md](../ARCHITECTURE.md) are capitalized on first use in a section when ambiguity is possible
- Diagrams use Mermaid unless a static image is required for publication
- ADRs are never silently rewritten; supersede with a new ADR
- Operational procedures must be runnable, not aspirational

## Status

Documentation tracks the architecture as designed for milestones on [ROADMAP.md](../ROADMAP.md). Where implementation has not landed yet, documents describe **intended contracts** so clients and contributors can build against a stable design.
