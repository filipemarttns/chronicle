"""PostgreSQL event store and outbox adapters."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from chronicle_adapters.persistence.models import EventRow, OutboxRow
from chronicle_domain.capture.envelope import (
    EventEnvelope,
    EventType,
    IdempotencyKey,
    SchemaVersion,
    SourceName,
)
from chronicle_domain.ports import AppendResult
from chronicle_domain.shared.ids import (
    ActorId,
    DeviceId,
    EventId,
    StoreOffset,
    WorkspaceId,
)


def _row_to_envelope(row: EventRow) -> EventEnvelope:
    return EventEnvelope(
        event_id=EventId(row.id),
        type=EventType(row.type),
        schema_version=SchemaVersion(row.schema_version),
        occurred_at=row.occurred_at,
        source=SourceName(row.source),
        actor_id=ActorId(row.actor_id),
        workspace_id=WorkspaceId(row.workspace_id),
        device_id=DeviceId(row.device_id),
        idempotency_key=IdempotencyKey(row.idempotency_key),
        payload=row.payload,
        correlation_id=row.correlation_id,
        causation_id=row.causation_id,
    )


class SqlAlchemyEventStore:
    """Append-only event store backed by PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, envelope: EventEnvelope) -> AppendResult:
        existing = self.get_by_idempotency(envelope.workspace_id, envelope.idempotency_key.value)
        if existing is not None:
            existing_envelope, _fp, offset = existing
            return AppendResult(
                event_id=existing_envelope.event_id,
                store_offset=offset,
                created=False,
            )

        row = EventRow(
            id=envelope.event_id.value,
            workspace_id=envelope.workspace_id.value,
            actor_id=envelope.actor_id.value,
            device_id=envelope.device_id.value,
            type=envelope.type.value,
            schema_version=envelope.schema_version.value,
            source=envelope.source.value,
            idempotency_key=envelope.idempotency_key.value,
            occurred_at=envelope.occurred_at,
            received_at=datetime.now(timezone.utc),
            correlation_id=envelope.correlation_id,
            causation_id=envelope.causation_id,
            payload=dict(envelope.payload),
            payload_fingerprint=envelope.payload_fingerprint(),
            redaction_meta=None,
        )
        self._session.add(row)
        self._session.flush()
        return AppendResult(
            event_id=EventId(row.id),
            store_offset=StoreOffset(int(row.store_offset)),
            created=True,
        )

    def get(self, event_id: EventId) -> EventEnvelope | None:
        row = self._session.scalar(select(EventRow).where(EventRow.id == event_id.value))
        return _row_to_envelope(row) if row else None

    def get_by_idempotency(
        self, workspace_id: WorkspaceId, key: str
    ) -> tuple[EventEnvelope, str, StoreOffset] | None:
        row = self._session.scalar(
            select(EventRow).where(
                EventRow.workspace_id == workspace_id.value,
                EventRow.idempotency_key == key,
            )
        )
        if row is None:
            return None
        return _row_to_envelope(row), row.payload_fingerprint, StoreOffset(int(row.store_offset))

    def read_from(
        self, workspace_id: WorkspaceId, offset: StoreOffset, limit: int
    ) -> list[tuple[EventEnvelope, StoreOffset]]:
        rows = self._session.scalars(
            select(EventRow)
            .where(
                EventRow.workspace_id == workspace_id.value,
                EventRow.store_offset > offset.value,
            )
            .order_by(EventRow.store_offset.asc())
            .limit(limit)
        ).all()
        return [(_row_to_envelope(row), StoreOffset(int(row.store_offset))) for row in rows]


class SqlAlchemyOutbox:
    def __init__(self, session: Session) -> None:
        self._session = session

    def enqueue(self, event_id: EventId, job_type: str = "project_event") -> None:
        self._session.add(
            OutboxRow(
                event_id=event_id.value,
                job_type=job_type,
                status="pending",
                available_at=datetime.now(timezone.utc),
            )
        )

    def claim_batch(self, limit: int = 50) -> list[tuple[int, UUID, str]]:
        rows = self._session.scalars(
            select(OutboxRow)
            .where(OutboxRow.status == "pending")
            .order_by(OutboxRow.id.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        ).all()
        claimed: list[tuple[int, UUID, str]] = []
        for row in rows:
            row.status = "processing"
            row.attempts += 1
            claimed.append((int(row.id), row.event_id, row.job_type))
        self._session.flush()
        return claimed

    def mark_published(self, outbox_id: int) -> None:
        row = self._session.get(OutboxRow, outbox_id)
        if row is not None:
            row.status = "done"

    def mark_done_for_event(self, event_id: EventId) -> None:
        rows = self._session.scalars(
            select(OutboxRow).where(
                OutboxRow.event_id == event_id.value,
                OutboxRow.status.in_(("pending", "processing")),
            )
        ).all()
        for row in rows:
            row.status = "done"

    def mark_failed(self, outbox_id: int, error: str) -> None:
        row = self._session.get(OutboxRow, outbox_id)
        if row is not None:
            row.status = "pending"
            row.last_error = error[:2000]
