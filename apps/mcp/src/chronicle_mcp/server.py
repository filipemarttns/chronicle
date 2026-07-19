"""Chronicle MCP server — search, timeline, and session summary tools."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from chronicle_api.container import get_container


def _redact(text: str) -> str:
    # Defense in depth; ingest already redacts, but tool egress scrubs common tokens.
    import re

    text = re.sub(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*", "Bearer [REDACTED:bearer]", text)
    return text


def tool_search_memory(workspace_id: str, query: str, limit: int = 10) -> dict[str, Any]:
    container = get_container()
    hits = container.search(UUID(workspace_id), query, limit=limit)
    return {
        "hits": [
            {
                "chunk_id": str(hit.chunk_id),
                "score": hit.score,
                "snippet": _redact(hit.snippet),
                "citations": [str(c) for c in hit.citations],
            }
            for hit in hits
        ]
    }


def tool_get_timeline(workspace_id: str, limit: int = 50) -> dict[str, Any]:
    container = get_container()
    items = container.replay(UUID(workspace_id), limit=limit)
    return {
        "items": [
            {
                "event_id": str(item.event_id),
                "type": item.type,
                "occurred_at": item.occurred_at.isoformat(),
                "summary": _redact(item.summary or item.type),
            }
            for item in items
        ]
    }


def tool_get_session_summary(workspace_id: str) -> dict[str, Any]:
    container = get_container()
    now = datetime.now(timezone.utc)
    summary = container.analytics_summary(UUID(workspace_id), now - timedelta(days=7), now)
    return {
        "workspace_id": summary.workspace_id,
        "window_days": 7,
        "metrics": summary.metrics,
        "narrative": _redact(
            f"{int(summary.metrics.get('session_count', 0))} sessions, "
            f"{int(summary.metrics.get('event_count', 0))} events, "
            f"{summary.metrics.get('focus_minutes', 0):.1f} focus minutes."
        ),
    }


TOOLS = {
    "search_memory": tool_search_memory,
    "get_timeline": tool_get_timeline,
    "get_session_summary": tool_get_session_summary,
}


def invoke_tool(name: str, arguments: dict[str, Any]) -> str:
    if name not in TOOLS:
        raise KeyError(f"unknown tool: {name}")
    result = TOOLS[name](**arguments)
    return json.dumps(result)


def main() -> None:
    """Minimal stdio loop for local MCP experimentation."""

    print("chronicle-mcp ready", flush=True)
    print("tools:" + ",".join(TOOLS), flush=True)
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            continue
        payload = json.loads(line)
        name = payload["tool"]
        args = payload.get("arguments", {})
        print(invoke_tool(name, args), flush=True)


if __name__ == "__main__":
    main()
