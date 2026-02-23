# ADR-0017: MCP Tool Surface and Redaction

- Status: Accepted
- Date: 2026-02-20
- Deciders: Lead Maintainer
- Tags: mcp, security, memory

## Context

Model Context Protocol clients can turn Chronicle into memory for assistants. Unfiltered tool responses could exfiltrate secrets, private URLs, or unrelated workspace data into third-party model providers.

## Decision

Expose Chronicle through a dedicated **MCP server** with a small, purpose-built tool set (search, timeline fetch, graph neighbors, session summary). Every tool invocation:

1. Authenticates as a principal with workspace scope
2. Applies consent and ACL filters
3. Runs **redaction** policies before returning text
4. Emits an audit event (`ToolInvocation`) with parameters hashed/summarized

Tools return citations (event ids) so assistants can ground claims without dumping raw high-risk payloads by default.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Raw SQL / event dump tools | Unsafe default |
| Embedding Chronicle only inside one vendor assistant | Undermines open protocol strategy |
| No MCP until late | Blocks AI memory milestone validation |

## Consequences

- Redaction policy becomes a product surface with tests.
- Operators must understand that MCP clients may forward data to external models—document residual risk.
- Tool schemas versioned like APIs.

## References

- ADR-0012, ADR-0021
- [api/mcp.md](../api/mcp.md)
