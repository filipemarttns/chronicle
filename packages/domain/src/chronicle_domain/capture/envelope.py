"""Event envelope value objects and construction."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from chronicle_domain.shared.ids import (
    ActorId,
    DeviceId,
    DomainValidationError,
    EventId,
    WorkspaceId,
)

_EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


@dataclass(frozen=True, slots=True)
class EventType:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > 128 or not _EVENT_TYPE_RE.match(self.value):
            raise DomainValidationError(f"invalid event type: {self.value!r}")


@dataclass(frozen=True, slots=True)
class SchemaVersion:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise DomainValidationError("schema_version must be >= 1")


@dataclass(frozen=True, slots=True)
class IdempotencyKey:
    value: str

    def __post_init__(self) -> None:
        if not (8 <= len(self.value) <= 200):
            raise DomainValidationError("idempotency key length out of range")


@dataclass(frozen=True, slots=True)
class SourceName:
    value: str

    def __post_init__(self) -> None:
        allowed = {
            "vscode",
            "cursor",
            "browser",
            "desktop",
            "api",
            "sync",
            "system",
            "git-hook",
        }
        if self.value not in allowed:
            raise DomainValidationError(f"unknown source: {self.value!r}")


def canonical_payload_fingerprint(payload: Mapping[str, Any]) -> str:
    """Return SHA-256 hex digest of canonical JSON payload."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Immutable capture or domain event envelope prior to persistence offsets."""

    event_id: EventId
    type: EventType
    schema_version: SchemaVersion
    occurred_at: datetime
    source: SourceName
    actor_id: ActorId
    workspace_id: WorkspaceId
    device_id: DeviceId
    idempotency_key: IdempotencyKey
    payload: Mapping[str, Any]
    correlation_id: str | None = None
    causation_id: str | None = None

    def payload_fingerprint(self) -> str:
        return canonical_payload_fingerprint(self.payload)
