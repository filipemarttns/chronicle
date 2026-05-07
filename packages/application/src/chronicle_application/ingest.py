"""Ingest application service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from chronicle_domain.capture.envelope import (
    EventEnvelope,
    EventType,
    IdempotencyKey,
    SchemaVersion,
    SourceName,
)
from chronicle_domain.capture.redaction import SecretRedactionService
from chronicle_domain.ports import AppendResult, ConsentPolicyPort, EventStorePort, OutboxPort
from chronicle_domain.shared.ids import (
    ActorId,
    DeviceId,
    DomainError,
    DomainValidationError,
    EventId,
    WorkspaceId,
)


@dataclass(frozen=True, slots=True)
class IngestEventCommand:
    type: str
    schema_version: int
    occurred_at: datetime
    source: str
    actor_id: UUID
    workspace_id: UUID
    device_id: UUID
    idempotency_key: str
    payload: Mapping[str, Any]
    event_id: UUID | None = None
    correlation_id: str | None = None
    causation_id: str | None = None


@dataclass(frozen=True, slots=True)
class IngestResult:
    event_id: UUID
    store_offset: int
    created: bool
    redaction_counts: Mapping[str, int]


class IdempotencyConflictError(DomainError):
    """Idempotency key reused with a different payload fingerprint."""


class IngestService:
    """Validate, redact, and append events with idempotency."""

    def __init__(
        self,
        event_store: EventStorePort,
        outbox: OutboxPort,
        consent_policies: ConsentPolicyPort,
        redactor: SecretRedactionService | None = None,
    ) -> None:
        self._event_store = event_store
        self._outbox = outbox
        self._consent_policies = consent_policies
        self._redactor = redactor or SecretRedactionService()

    def ingest(self, command: IngestEventCommand) -> IngestResult:
        event_type = EventType(command.type)
        workspace_id = WorkspaceId(command.workspace_id)
        policy = self._consent_policies.get(workspace_id)
        policy.allow(event_type)

        redacted = self._redactor.redact_payload(dict(command.payload))
        event_id = EventId(command.event_id) if command.event_id else EventId(self._new_id())
        envelope = EventEnvelope(
            event_id=event_id,
            type=event_type,
            schema_version=SchemaVersion(command.schema_version),
            occurred_at=command.occurred_at,
            source=SourceName(command.source),
            actor_id=ActorId(command.actor_id),
            workspace_id=workspace_id,
            device_id=DeviceId(command.device_id),
            idempotency_key=IdempotencyKey(command.idempotency_key),
            payload=redacted.value,
            correlation_id=command.correlation_id,
            causation_id=command.causation_id,
        )

        existing = self._event_store.get_by_idempotency(
            workspace_id, command.idempotency_key
        )
        if existing is not None:
            existing_envelope, fingerprint, offset = existing
            if fingerprint != envelope.payload_fingerprint():
                raise IdempotencyConflictError(
                    "idempotency key reused with different payload"
                )
            return IngestResult(
                event_id=existing_envelope.event_id.value,
                store_offset=offset.value,
                created=False,
                redaction_counts=redacted.counts,
            )

        result: AppendResult = self._event_store.append(envelope)
        if result.created:
            self._outbox.enqueue(result.event_id, "project_event")
        return IngestResult(
            event_id=result.event_id.value,
            store_offset=result.store_offset.value,
            created=result.created,
            redaction_counts=redacted.counts,
        )

    def _new_id(self) -> UUID:
        from uuid import uuid4

        return uuid4()
