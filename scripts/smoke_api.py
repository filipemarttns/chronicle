#!/usr/bin/env python3
"""Smoke the local Chronicle API: health → consent → ingest → timeline → search."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
API = os.getenv("CHRONICLE_API_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.getenv("CHRONICLE_API_TOKEN", "")
FIXTURE = ROOT / "scripts" / "fixtures" / "sample_event.json"


def request(method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as res:
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def main() -> int:
    try:
        health = request("GET", "/health")
    except urllib.error.URLError as exc:
        print(f"API unreachable at {API}: {exc}", file=sys.stderr)
        return 1

    if health.get("status") != "ok":
        print(f"unexpected health payload: {health}", file=sys.stderr)
        return 1
    print("health ok")

    event = json.loads(FIXTURE.read_text(encoding="utf-8"))
    event["idempotency_key"] = f"smoke-{uuid4().hex[:12]}"
    workspace_id = event["workspace_id"]

    request(
        "PUT",
        "/v1/consent",
        {
            "workspace_id": workspace_id,
            "categories": {
                "editor": True,
                "terminal": False,
                "git": False,
                "browser": False,
                "assistant": False,
                "build": False,
            },
        },
    )
    print("consent ok")

    ingested = request("POST", "/v1/events", event)
    print(f"ingest ok event_id={ingested.get('event_id')}")

    timeline = request(
        "GET",
        f"/v1/timelines/replay?workspace_id={workspace_id}&limit=10",
    )
    items = timeline.get("items") or []
    if not items:
        print("timeline returned no items", file=sys.stderr)
        return 1
    print(f"timeline ok items={len(items)}")

    search = request(
        "POST",
        "/v1/search",
        {"workspace_id": workspace_id, "query": "indexer.py", "limit": 5},
    )
    hits = search.get("hits") or []
    if not hits:
        print("search returned no hits", file=sys.stderr)
        return 1
    print(f"search ok hits={len(hits)}")
    print("smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
