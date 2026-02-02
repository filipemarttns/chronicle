"""API smoke tests."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from chronicle_api.main import app, reset_state


def setup_function() -> None:
    reset_state()


def test_health() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"


def test_ingest_and_replay_and_search() -> None:
    client = TestClient(app)
    workspace_id = str(uuid4())
    actor_id = str(uuid4())
    device_id = str(uuid4())

    consent = client.put(
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
    )
    assert consent.status_code == 200

    payload = {
        "type": "editor.file.opened",
        "schema_version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "source": "vscode",
        "actor_id": actor_id,
        "workspace_id": workspace_id,
        "device_id": device_id,
        "idempotency_key": "api-test-idem-0001",
        "payload": {"path": "apps/api/src/main.py", "language": "python"},
    }
    created = client.post("/v1/events", json=payload)
    assert created.status_code == 200
    body = created.json()
    assert body["created"] is True

    replay = client.get("/v1/timelines/replay", params={"workspace_id": workspace_id})
    assert replay.status_code == 200
    assert len(replay.json()["items"]) == 1

    search = client.post(
        "/v1/search",
        json={"workspace_id": workspace_id, "query": "main.py python", "limit": 5},
    )
    assert search.status_code == 200
    assert len(search.json()["hits"]) >= 1
