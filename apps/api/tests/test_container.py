"""Tests for outbox projector helpers using in-memory pathway compatibility."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from chronicle_api.container import reset_container_for_tests
from chronicle_application.ingest import IngestEventCommand


def test_container_memory_ingest_projects_timeline_and_search() -> None:
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
    result = container.ingest(
        IngestEventCommand(
            type="editor.file.opened",
            schema_version=1,
            occurred_at=datetime.now(timezone.utc),
            source="vscode",
            actor_id=uuid4(),
            workspace_id=workspace_id,
            device_id=uuid4(),
            idempotency_key="container-idem-0001",
            payload={"path": "packages/domain/src/session.py", "language": "python"},
        )
    )
    assert result.created is True
    items = container.replay(workspace_id)
    assert len(items) == 1
    hits = container.search(workspace_id, "session.py")
    assert len(hits) >= 1
    assert container.process_outbox() == 0
