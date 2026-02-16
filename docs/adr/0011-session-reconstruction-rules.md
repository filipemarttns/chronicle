# ADR-0011: Session Reconstruction Rules

- Status: Accepted
- Date: 2026-02-03
- Deciders: Lead Maintainer
- Tags: domain, session, timeline

## Context

Raw events are too fine-grained for human replay. Chronicle must cluster activity into **Sessions** without inventing false narrative. Rules must be deterministic so rebuilds converge.

## Decision

Define Session reconstruction as a pure function of ordered events plus configuration:

1. **Open** a session on the first eligible activity event for `(workspace_id, device_id)` when none is open.
2. **Idle gap**: close a session when wall-clock gap since last eligible event exceeds `session_idle_timeout` (default 30 minutes, configurable per workspace).
3. **Workspace switch**: events for a different workspace do not extend the prior workspace session.
4. **Explicit markers**: optional `session.marker` events force open/close.
5. **Assignment**: each eligible event references at most one session id in the projection.
6. **Corrections**: merges/splits append compensating domain events; they do not mutate past telemetry.

Ineligible events (pure heartbeats, if any) do not extend idle timers.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Calendar-day sessions only | Too coarse for replay |
| ML clustering as source of truth | Non-deterministic rebuilds |
| Manual sessions only | High friction; incomplete capture |

## Consequences

- Timeout changes require projection rebuild or versioned session algorithm id on summaries.
- Analytics must key off algorithm version.
- Document defaults in operator guides.

## References

- ADR-0001, ADR-0002
- [architecture/bounded-contexts.md](../architecture/bounded-contexts.md)
