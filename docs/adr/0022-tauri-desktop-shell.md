# ADR-0022: Tauri for Desktop Control Plane

- Status: Accepted
- Date: 2026-03-08
- Deciders: Lead Maintainer
- Tags: desktop, clients

## Context

Chronicle needs a desktop shell for timeline review, consent management, local service control, and notifications—without the memory footprint and packaging model of a full Electron stack when a lighter WebView approach suffices.

## Decision

Build the desktop control plane with **Tauri**, reusing web UI packages where practical, while treating the Chronicle API as a network boundary (even on localhost).

Native responsibilities: secure token storage integrations, autostart optional hooks, system tray presence, and packaging for major desktop OSes.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Electron | Higher baseline resource cost for a long-running tray app |
| Pure native UI per OS | Triples UI engineering cost |
| Web-only, no desktop | Weaker local control and discovery for non-technical operators |

## Consequences

- Rust toolchain required for contributors to the desktop app.
- Security review must include WebView IPC boundaries.
- Feature parity with web console is not required; desktop prioritizes control-plane workflows.

## References

- ADR-0013
- [architecture/clients.md](../architecture/clients.md)
