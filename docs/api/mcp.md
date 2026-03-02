# MCP API

Chronicle’s Model Context Protocol server exposes memory tools with mandatory redaction and audit (ADR-0017).

## Tools (initial set)

| Tool | Purpose | Returns |
| --- | --- | --- |
| `search_memory` | Semantic/hybrid search | Ranked hits + event citations |
| `get_timeline` | Replay window or session | Ordered items (redacted) |
| `get_session_summary` | Compressed session narrative | Summary + citations |
| `graph_neighbors` | Structural neighbors | Nodes/edges + evidence ids |

## Invocation policy

1. Authenticate
2. Enforce workspace scope
3. Apply consent filters
4. Redact outbound text
5. Audit `ToolInvocation`

## Residual risk notice

MCP clients may send tool results to third-party model providers. Operators enabling MCP must treat this as an intentional data egress path.
