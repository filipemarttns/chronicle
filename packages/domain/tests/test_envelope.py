"""Domain tests for event envelope and redaction."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from chronicle_domain.capture.envelope import (
    EventEnvelope,
    EventType,
    IdempotencyKey,
    SchemaVersion,
    SourceName,
    canonical_payload_fingerprint,
)
from chronicle_domain.capture.redaction import SecretRedactionService
from chronicle_domain.shared.ids import (
    ActorId,
    DeviceId,
    DomainValidationError,
    EventId,
    WorkspaceId,
)


def test_event_type_rejects_invalid() -> None:
    with pytest.raises(DomainValidationError):
        EventType("Not Valid")


def test_idempotency_key_bounds() -> None:
    with pytest.raises(DomainValidationError):
        IdempotencyKey("short")


def test_payload_fingerprint_stable() -> None:
    a = canonical_payload_fingerprint({"b": 1, "a": 2})
    b = canonical_payload_fingerprint({"a": 2, "b": 1})
    assert a == b


def test_redacts_bearer_token() -> None:
    service = SecretRedactionService()
    result = service.redact_string("Authorization: Bearer super-secret-token-value")
    assert "super-secret-token-value" not in result.value
    assert result.counts.get("bearer", 0) >= 1


def test_envelope_fingerprint_uses_payload() -> None:
    envelope = EventEnvelope(
        event_id=EventId(uuid4()),
        type=EventType("editor.file.opened"),
        schema_version=SchemaVersion(1),
        occurred_at=datetime.now(timezone.utc),
        source=SourceName("vscode"),
        actor_id=ActorId(uuid4()),
        workspace_id=WorkspaceId(uuid4()),
        device_id=DeviceId(uuid4()),
        idempotency_key=IdempotencyKey("idem-key-001"),
        payload={"path": "a.py"},
    )
    assert len(envelope.payload_fingerprint()) == 64
