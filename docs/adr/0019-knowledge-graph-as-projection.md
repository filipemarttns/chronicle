# ADR-0019: Knowledge Graph as Rebuildable Projection

- Status: Accepted
- Date: 2026-03-02
- Deciders: Lead Maintainer
- Tags: graph, projection

## Context

Chronicle must answer relationship questions (“what PRs touched this module while this ADR was open?”). Storing graph edges as source of truth would fork reality from the event log.

## Decision

The **knowledge graph is a projection**:

- Nodes and edges are derived from events by deterministic projectors.
- Each edge stores evidence pointers (`event_id` list) for explainability.
- Full rebuild from the event log must be supported.
- Graph query APIs never accept client-written edges as durable facts (annotations may be modeled as events).

Storage remains in PostgreSQL tables for v1 (not a separate graph DB).

## Alternatives Considered

| Alternative | Why rejected for v1 |
| --- | --- |
| Neo4j/Memgraph as system of record | Dual truth; ops overhead |
| Only vector search, no graph | Weak structural navigation |
| Manual wiki graph | Not automatic from engineering activity |

## Consequences

- Graph schema evolves with projector versions.
- Deep traversals need indexed adjacency and depth limits.
- Evidence pointers increase storage slightly; worth it for trust.

## References

- ADR-0001, ADR-0002
- [architecture/knowledge-graph.md](../architecture/knowledge-graph.md)
