"""API coverage for sessions, analytics, and sync."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from chronicle_api.main import app, reset_state


def setup_function() -> None:
    reset_state()


def test_sessions_analytics_and_sync_roundtrip() -> None:
    client = TestClient(app)
    workspace_id = str(uuid4())
    actor_id = str(uuid4())
    device_id = str(uuid4())
    now = datetime.now(timezone.utc)

    assert (
        client.put(
            "/v1/consent",
            json={
                "workspace_id": workspace_id,
                "categories": {
                    "editor": True,
                    "terminal": True,
                    "git": True,
                    "browser": False,
                    "assistant": False,
                    "build": True,
                },
            },
        ).status_code
        == 200
    )

    created = client.post(
        "/v1/events",
        json={
            "type": "editor.file.opened",
            "schema_version": 1,
            "occurred_at": now.isoformat(),
            "source": "vscode",
            "actor_id": actor_id,
            "workspace_id": workspace_id,
            "device_id": device_id,
            "idempotency_key": "sync-roundtrip-0001",
            "payload": {"path": "apps/api/src/main.py", "language": "python"},
        },
    )
    assert created.status_code == 200

    sessions = client.get("/v1/sessions", params={"workspace_id": workspace_id})
    assert sessions.status_code == 200
    assert len(sessions.json()["items"]) >= 1

    summary = client.get(
        "/v1/analytics/summary",
        params={
            "workspace_id": workspace_id,
            "from": (now - timedelta(days=1)).isoformat(),
            "to": (now + timedelta(hours=1)).isoformat(),
        },
    )
    assert summary.status_code == 200
    assert summary.json()["metrics"]["event_count"] >= 1

    pull = client.post(
        "/v1/sync/pull",
        json={
            "workspace_id": workspace_id,
            "device_id": device_id,
            "cursor": 0,
            "limit": 10,
        },
    )
    assert pull.status_code == 200
    assert len(pull.json()["events"]) >= 1

    push = client.post(
        "/v1/sync/push",
        json={
            "workspace_id": workspace_id,
            "device_id": device_id,
            "events": [
                {
                    "type": "terminal.command.executed",
                    "schema_version": 1,
                    "occurred_at": now.isoformat(),
                    "source": "vscode",
                    "actor_id": actor_id,
                    "workspace_id": workspace_id,
                    "device_id": device_id,
                    "idempotency_key": "sync-push-cmd-0001",
                    "payload": {"command": "pytest -q", "exit_code": 0},
                }
            ],
        },
    )
    assert push.status_code == 200
    assert len(push.json()["accepted"]) == 1
