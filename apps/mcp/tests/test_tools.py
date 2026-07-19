"""MCP tool smoke tests."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from chronicle_api.container import reset_container_for_tests
from chronicle_application.ingest import IngestEventCommand
from chronicle_mcp.server import invoke_tool, tool_search_memory


def test_mcp_search_tool() -> None:
    container = reset_container_for_tests()
    workspace_id = uuid4()
    container.put_consent(
        workspace_id,
        {
            "editor": True,
            "terminal": False,
            "git": False,
            "browser": False,
            "assistant": False,
            "build": False,
        },
    )
    container.ingest(
        IngestEventCommand(
            type="editor.file.opened",
            schema_version=1,
            occurred_at=datetime.now(timezone.utc),
            source="vscode",
            actor_id=uuid4(),
            workspace_id=workspace_id,
            device_id=uuid4(),
            idempotency_key="mcp-tool-0001",
            payload={"path": "apps/mcp/src/server.py", "language": "python"},
        )
    )
    payload = tool_search_memory(str(workspace_id), "server.py", limit=5)
    assert len(payload["hits"]) >= 1
    raw = invoke_tool(
        "get_session_summary",
        {"workspace_id": str(workspace_id)},
    )
    assert "focus_minutes" in raw
