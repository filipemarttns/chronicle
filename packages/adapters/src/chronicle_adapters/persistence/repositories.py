"""SQLAlchemy repositories for consent, sessions, timeline, and memory."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from chronicle_adapters.persistence.models import (
    ConsentRow,
    MemoryChunkRow,
    SessionRow,
    TimelineItemRow,
)
from chronicle_application.memory import MemoryIndex, SearchHit
from chronicle_application.timeline import TimelineItem
from chronicle_domain.capture.envelope import EventEnvelope
from chronicle_domain.identity.consent import ConsentCategory, ConsentPolicy
from chronicle_domain.session.session import Session as DomainSession
from chronicle_domain.shared.ids import DeviceId, SessionId, StoreOffset, WorkspaceId


class SqlAlchemyConsentStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, workspace_id: WorkspaceId) -> ConsentPolicy:
        row = self._session.get(ConsentRow, workspace_id.value)
        if row is None:
            return ConsentPolicy(workspace_id=workspace_id)
        categories = {
            ConsentCategory(key): bool(value) for key, value in row.categories.items()
        }
        return ConsentPolicy(workspace_id=workspace_id, categories=categories)

    def save(self, policy: ConsentPolicy) -> None:
        payload = {key.value: enabled for key, enabled in policy.categories.items()}
        row = self._session.get(ConsentRow, policy.workspace_id.value)
        if row is None:
            row = ConsentRow(workspace_id=policy.workspace_id.value, categories=payload)
            self._session.add(row)
        else:
            row.categories = payload
        self._session.flush()


class SqlAlchemySessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, session: DomainSession) -> None:
        row = self._session.get(SessionRow, session.id.value)
        if row is None:
            row = SessionRow(
                id=session.id.value,
                workspace_id=session.workspace_id.value,
                device_id=session.device_id.value,
                started_at=session.started_at,
                last_activity_at=session.last_activity_at,
                ended_at=session.ended_at,
                algorithm_version=session.algorithm_version,
                is_open=session.is_open,
            )
            self._session.add(row)
        else:
            row.last_activity_at = session.last_activity_at
            row.ended_at = session.ended_at
            row.is_open = session.is_open
        self._session.flush()

    def get(self, session_id: SessionId) -> DomainSession | None:
        row = self._session.get(SessionRow, session_id.value)
        return self._to_domain(row) if row else None

    def find_open(self, workspace_id: WorkspaceId, device_id: DeviceId) -> DomainSession | None:
        row = self._session.scalar(
            select(SessionRow).where(
                SessionRow.workspace_id == workspace_id.value,
                SessionRow.device_id == device_id.value,
                SessionRow.is_open.is_(True),
            )
        )
        return self._to_domain(row) if row else None

    @staticmethod
    def _to_domain(row: SessionRow) -> DomainSession:
        return DomainSession(
            id=SessionId(row.id),
            workspace_id=WorkspaceId(row.workspace_id),
            device_id=DeviceId(row.device_id),
            started_at=row.started_at,
            last_activity_at=row.last_activity_at,
            ended_at=row.ended_at,
            algorithm_version=row.algorithm_version,
        )


class SqlAlchemyTimelineStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def apply(
        self,
        envelope: EventEnvelope,
        offset: StoreOffset,
        session_id: UUID | None = None,
    ) -> TimelineItem:
        item = TimelineItem(
            event_id=envelope.event_id.value,
            type=envelope.type.value,
            occurred_at=envelope.occurred_at,
            source=envelope.source.value,
            store_offset=offset.value,
            session_id=session_id,
            summary=envelope.type.value,
            payload_preview=dict(list(envelope.payload.items())[:5]),
        )
        existing = self._session.scalar(
            select(TimelineItemRow).where(TimelineItemRow.event_id == envelope.event_id.value)
        )
        if existing is None:
            self._session.add(
                TimelineItemRow(
                    workspace_id=envelope.workspace_id.value,
                    event_id=item.event_id,
                    session_id=session_id,
                    type=item.type,
                    source=item.source,
                    occurred_at=item.occurred_at,
                    store_offset=item.store_offset,
                    summary=item.summary,
                    payload_preview=item.payload_preview,
                )
            )
            self._session.flush()
        return item

    def replay(
        self,
        workspace_id: WorkspaceId,
        *,
        limit: int = 50,
        after_offset: int = 0,
    ) -> list[TimelineItem]:
        rows = self._session.scalars(
            select(TimelineItemRow)
            .where(
                TimelineItemRow.workspace_id == workspace_id.value,
                TimelineItemRow.store_offset > after_offset,
            )
            .order_by(TimelineItemRow.store_offset.asc())
            .limit(limit)
        ).all()
        return [
            TimelineItem(
                event_id=row.event_id,
                type=row.type,
                occurred_at=row.occurred_at,
                source=row.source,
                store_offset=int(row.store_offset),
                session_id=row.session_id,
                summary=row.summary,
                payload_preview=row.payload_preview,
            )
            for row in rows
        ]


class SqlAlchemyMemoryIndex:
    """Persisted chunk index with token-overlap search (pgvector lands later)."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._local = MemoryIndex()

    def index_event(self, envelope: EventEnvelope) -> None:
        content = f"{envelope.type.value} " + " ".join(
            f"{k}={v}" for k, v in envelope.payload.items() if isinstance(v, (str, int))
        )
        existing = self._session.scalar(
            select(MemoryChunkRow).where(MemoryChunkRow.event_id == envelope.event_id.value)
        )
        if existing is None:
            self._session.add(
                MemoryChunkRow(
                    id=uuid4(),
                    workspace_id=envelope.workspace_id.value,
                    event_id=envelope.event_id.value,
                    content=content.lower(),
                )
            )
            self._session.flush()

    def search(
        self, query: str, *, workspace_id: UUID | None = None, limit: int = 10
    ) -> list[SearchHit]:
        stmt = select(MemoryChunkRow)
        if workspace_id is not None:
            stmt = stmt.where(MemoryChunkRow.workspace_id == workspace_id)
        rows = self._session.scalars(stmt.limit(5000)).all()
        index = MemoryIndex()
        for row in rows:
            index._chunks.append((row.id, row.content, (row.event_id,)))
        return index.search(query, limit=limit)
