# Knowledge Graph Architecture

## Purpose

Provide structural navigation over engineering artifacts with **explainable** edges grounded in Events.

## Node types (initial)

| node_type | external_key examples |
| --- | --- |
| `file` | workspace-relative path |
| `symbol` | `path::qualified_name` |
| `commit` | git commit SHA |
| `pull_request` | host/repo#number |
| `session` | session UUID |
| `decision` | ADR id / decision slug |
| `actor` | actor UUID |
| `url` | normalized URL (browser opt-in) |

## Edge types (initial)

| edge_type | Meaning |
| --- | --- |
| `touched` | session/commit touched file |
| `implements` | commit implements decision |
| `reviews` | actor reviews PR |
| `caused_by` | failure linked to prior change evidence |
| `references` | file/ADR references URL or decision |
| `contains` | commit contains file change |

## Evidence

Every edge stores one or more `event_id`s. UI and MCP responses should surface evidence so answers are falsifiable.

## Rebuild

Graph tables are disposable. Projector version bumps that change topology require rebuild. See ADR-0019.

## Query limits

- Default neighbor depth: 1–2
- Hard max depth: 4
- Result caps prevent runaway traversals on dense file hubs
