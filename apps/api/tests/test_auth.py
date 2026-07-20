"""Auth and hashing embedder tests."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

import chronicle_api.container as container_mod
from chronicle_api.config import Settings
from chronicle_api.container import AppContainer
from chronicle_api.main import app, reset_state
from chronicle_application.auth import hash_token
from chronicle_application.embeddings import HashingEmbedder, cosine_similarity


def setup_function() -> None:
    reset_state()


def test_hash_token_stable() -> None:
    assert hash_token("abc", pepper="p") == hash_token("abc", pepper="p")
    assert hash_token("abc", pepper="p") != hash_token("abc", pepper="q")


def test_hashing_embedder_normalized() -> None:
    embedder = HashingEmbedder(dims=64)
    vector = embedder.embed("editor.file.opened path=main.py")
    assert len(vector) == 64
    norm = sum(v * v for v in vector) ** 0.5
    assert abs(norm - 1.0) < 1e-6
    assert cosine_similarity(vector, vector) > 0.99


def test_token_auth_rejects_missing_bearer() -> None:
    container_mod._container = AppContainer(
        settings=Settings(store_mode="memory", auth_mode="token", bootstrap_token="x")
    )
    container_mod._container.configure()
    client = TestClient(app)
    res = client.get("/v1/sessions", params={"workspace_id": str(uuid4())})
    assert res.status_code == 401


def test_issue_and_use_token() -> None:
    container_mod._container = AppContainer(
        settings=Settings(
            store_mode="memory",
            auth_mode="token",
            bootstrap_token="bootstrap-secret",
            auth_pepper="pepper",
        )
    )
    container_mod._container.configure()
    client = TestClient(app)
    workspace_id = str(uuid4())
    actor_id = str(uuid4())
    issued = client.post(
        "/v1/auth/tokens",
        headers={"X-Chronicle-Bootstrap": "bootstrap-secret"},
        json={"workspace_id": workspace_id, "actor_id": actor_id, "label": "ci"},
    )
    assert issued.status_code == 200
    token = issued.json()["token"]
    denied = client.get("/v1/sessions", params={"workspace_id": workspace_id})
    assert denied.status_code == 401
    ok = client.get(
        "/v1/sessions",
        params={"workspace_id": workspace_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ok.status_code == 200
    other = client.get(
        "/v1/sessions",
        params={"workspace_id": str(uuid4())},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert other.status_code == 403


def test_cors_allows_local_web_origin() -> None:
    client = TestClient(app)
    res = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code in {200, 204}
    assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"
