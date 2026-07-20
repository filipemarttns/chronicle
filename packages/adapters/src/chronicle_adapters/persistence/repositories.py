"""SQLAlchemy repositories for consent, sessions, timeline, memory, and credentials."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from chronicle_adapters.persistence.models import (
    ConsentRow,
    CredentialRow,
    MemoryChunkRow,
    SessionRow,
    TimelineItemRow,
)
from chronicle_application.auth import CredentialRecord, CredentialService, IssuedCredential
from chronicle_application.embeddings import HashingEmbedder
from chronicle_application.memory import MemoryIndex, SearchHit, event_text
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

    def list_for_workspace(self, workspace_id: WorkspaceId) -> list[DomainSession]:
        rows = self._session.scalars(
            select(SessionRow)
            .where(SessionRow.workspace_id == workspace_id.value)
            .order_by(SessionRow.started_at.desc())
        ).all()
        return [self._to_domain(row) for row in rows]

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
    """Persisted chunk index with hashing embeddings stored in pgvector when available."""

    def __init__(
        self,
        session: Session,
        embedder: HashingEmbedder | None = None,
        *,
        use_pgvector: bool = True,
    ) -> None:
        self._session = session
        self._embedder = embedder or HashingEmbedder()
        self._use_pgvector = use_pgvector

    def index_event(self, envelope: EventEnvelope) -> None:
        content = event_text(envelope)
        vector = self._embedder.embed(content)
        existing = self._session.scalar(
            select(MemoryChunkRow).where(MemoryChunkRow.event_id == envelope.event_id.value)
        )
        if existing is None:
            self._session.add(
                MemoryChunkRow(
                    id=uuid4(),
                    workspace_id=envelope.workspace_id.value,
                    event_id=envelope.event_id.value,
                    content=content,
                    model_id=self._embedder.model_id,
                    embedding=vector,
                )
            )
            self._session.flush()

    def search(
        self, query: str, *, workspace_id: UUID | None = None, limit: int = 10
    ) -> list[SearchHit]:
        query_vec = self._embedder.embed(query.lower())
        if self._use_pgvector and workspace_id is not None:
            try:
                return self._search_pgvector_simple(
                    query_vec, workspace_id=workspace_id, limit=limit
                )
            except Exception:
                # Extension/index may be unavailable; fall back.
                pass
        stmt = select(MemoryChunkRow)
        if workspace_id is not None:
            stmt = stmt.where(MemoryChunkRow.workspace_id == workspace_id)
        rows = self._session.scalars(stmt.limit(5000)).all()
        index = MemoryIndex(embedder=self._embedder)
        for row in rows:
            vector = list(row.embedding) if row.embedding is not None else self._embedder.embed(row.content)
            index._chunks.append((row.id, row.content, (row.event_id,), vector))
        return index.search(query, limit=limit)

    def _search_pgvector_simple(
        self, query_vec: list[float], *, workspace_id: UUID, limit: int
    ) -> list[SearchHit]:
        from chronicle_application.embeddings import cosine_similarity

        rows = self._session.scalars(
            select(MemoryChunkRow)
            .where(
                MemoryChunkRow.workspace_id == workspace_id,
                MemoryChunkRow.embedding.is_not(None),
            )
            .order_by(MemoryChunkRow.embedding.cosine_distance(query_vec))
            .limit(limit)
        ).all()
        hits: list[SearchHit] = []
        for row in rows:
            vector = list(row.embedding)
            score = cosine_similarity(query_vec, vector)
            hits.append(
                SearchHit(
                    chunk_id=row.id,
                    score=score,
                    snippet=row.content[:200],
                    citations=(row.event_id,),
                )
            )
        return hits


class SqlAlchemyCredentialStore:
    def __init__(self, session: Session, service: CredentialService) -> None:
        self._session = session
        self._service = service

    def save_issued(self, issued: IssuedCredential) -> None:
        self._session.add(
            CredentialRow(
                id=issued.credential_id,
                workspace_id=issued.workspace_id,
                actor_id=issued.actor_id,
                token_hash=issued.token_hash,
                label=issued.label,
                created_at=issued.created_at,
            )
        )
        self._session.flush()

    def find_by_raw_token(self, raw_token: str) -> CredentialRecord | None:
        from chronicle_application.auth import hash_token

        token_hash = hash_token(raw_token, pepper=self._service._pepper)
        row = self._session.scalar(
            select(CredentialRow).where(
                CredentialRow.token_hash == token_hash,
                CredentialRow.revoked_at.is_(None),
            )
        )
        if row is None:
            return None
        return CredentialRecord(
            credential_id=row.id,
            workspace_id=row.workspace_id,
            actor_id=row.actor_id,
            token_hash=row.token_hash,
            label=row.label,
            created_at=row.created_at,
            revoked_at=row.revoked_at,
        )