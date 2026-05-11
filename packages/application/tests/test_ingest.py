"""Ingest service integration-style tests with in-memory adapters."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from chronicle_adapters.memory import (
    InMemoryConsentPolicyStore,
    InMemoryEventStore,
    InMemoryOutbox,
)
from chronicle_application.ingest import (
    IdempotencyConflictError,
    IngestEventCommand,
    IngestService,
)
from chronicle_domain.shared.ids import ConsentDenied, WorkspaceId


def _command(**overrides):
    base = dict(
        type="editor.file.opened",
        schema_version=1,
        occurred_at=datetime.now(timezone.utc),
        source="vscode",
        actor_id=uuid4(),
        workspace_id=uuid4(),
        device_id=uuid4(),
        idempotency_key="idempotency-key-1",
        payload={"path": "main.py", "language": "python"},
    )
    base.update(overrides)
    return IngestEventCommand(**base)


def test_ingest_requires_consent() -> None:
    store = InMemoryEventStore()
    outbox = InMemoryOutbox()
    consent = InMemoryConsentPolicyStore()
    service = IngestService(store, outbox, consent)
    with pytest.raises(ConsentDenied):
        service.ingest(_command())


def test_ingest_appends_and_enqueues() -> None:
    store = InMemoryEventStore()
    outbox = InMemoryOutbox()
    consent = InMemoryConsentPolicyStore()
    cmd = _command()
    consent.enable_all(WorkspaceId(cmd.workspace_id))
    service = IngestService(store, outbox, consent)
    result = service.ingest(cmd)
    assert result.created is True
    assert result.store_offset == 1
    assert len(outbox.jobs) == 1


def test_ingest_idempotent_replay() -> None:
    store = InMemoryEventStore()
    outbox = InMemoryOutbox()
    consent = InMemoryConsentPolicyStore()
    cmd = _command()
    consent.enable_all(WorkspaceId(cmd.workspace_id))
    service = IngestService(store, outbox, consent)
    first = service.ingest(cmd)
    second = service.ingest(cmd)
    assert first.event_id == second.event_id
    assert second.created is False
    assert len(outbox.jobs) == 1


def test_ingest_idempotency_conflict() -> None:
    store = InMemoryEventStore()
    outbox = InMemoryOutbox()
    consent = InMemoryConsentPolicyStore()
    cmd = _command()
    consent.enable_all(WorkspaceId(cmd.workspace_id))
    service = IngestService(store, outbox, consent)
    service.ingest(cmd)
    with pytest.raises(IdempotencyConflictError):
        service.ingest(_command(
            workspace_id=cmd.workspace_id,
            actor_id=cmd.actor_id,
            device_id=cmd.device_id,
            idempotency_key=cmd.idempotency_key,
            payload={"path": "other.py"},
        ))
