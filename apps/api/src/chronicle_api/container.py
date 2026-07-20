"""Runtime dependency container for API and workers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from chronicle_adapters.memory import (
    InMemoryConsentPolicyStore,
    InMemoryCredentialStore,
    InMemoryEventStore,
    InMemoryOutbox,
    InMemorySessionRepository,
)
from chronicle_adapters.persistence import (
    OutboxProjector,
    PostgresIngestGateway,
    create_all,
    create_db_engine,
    create_session_factory,
)
from chronicle_adapters.persistence.repositories import (
    SqlAlchemyConsentStore,
    SqlAlchemyCredentialStore,
    SqlAlchemyMemoryIndex,
    SqlAlchemyTimelineStore,
)
from chronicle_api.config import Settings
from chronicle_application.auth import CredentialService, IssuedCredential
from chronicle_application.embeddings import HashingEmbedder
from chronicle_application.ingest import IngestEventCommand, IngestResult, IngestService
from chronicle_application.memory import MemoryIndex, SearchHit
from chronicle_application.session_projection import SessionProjector
from chronicle_application.timeline import TimelineItem, TimelineProjector
from chronicle_domain.identity.consent import ConsentCategory, ConsentPolicy
from chronicle_domain.shared.ids import EventId, StoreOffset, WorkspaceId


@dataclass
class AppContainer:
    settings: Settings
    mode: str = "memory"
    _session_factory: sessionmaker[Session] | None = None
    _pg_ingest: PostgresIngestGateway | None = None
    _outbox_projector: OutboxProjector | None = None
    credential_service: CredentialService = field(init=False)
    credentials: InMemoryCredentialStore = field(default_factory=InMemoryCredentialStore)
    embedder: HashingEmbedder = field(init=False)
    store: InMemoryEventStore = field(default_factory=InMemoryEventStore)
    outbox: InMemoryOutbox = field(default_factory=InMemoryOutbox)
    consent: InMemoryConsentPolicyStore = field(default_factory=InMemoryConsentPolicyStore)
    sessions: InMemorySessionRepository = field(default_factory=InMemorySessionRepository)
    timeline: TimelineProjector = field(default_factory=TimelineProjector)
    memory: MemoryIndex = field(init=False)
    ingest_service: IngestService | None = None
    session_projector: SessionProjector | None = None

    def __post_init__(self) -> None:
        self.credential_service = CredentialService(pepper=self.settings.auth_pepper)
        self.embedder = HashingEmbedder(dims=self.settings.embedding_dims)
        self.memory = MemoryIndex(embedder=self.embedder)

    def configure(self) -> None:
        if self.settings.store_mode == "postgres":
            engine = create_db_engine(self.settings.database_url)
            create_all(engine)
            self._session_factory = create_session_factory(engine)
            self._pg_ingest = PostgresIngestGateway(
                self._session_factory,
                sync_project=self.settings.sync_project,
                embedder=self.embedder,
            )
            self._outbox_projector = OutboxProjector(
                self._session_factory, embedder=self.embedder
            )
            self.mode = "postgres"
            return
        self.ingest_service = IngestService(self.store, self.outbox, self.consent)
        self.session_projector = SessionProjector(self.sessions)
        self.mode = "memory"

    def reset_memory(self) -> None:
        self.store = InMemoryEventStore()
        self.outbox = InMemoryOutbox()
        self.consent = InMemoryConsentPolicyStore()
        self.sessions = InMemorySessionRepository()
        self.credentials = InMemoryCredentialStore()
        self.timeline = TimelineProjector()
        self.memory = MemoryIndex(embedder=self.embedder)
        self.ingest_service = IngestService(self.store, self.outbox, self.consent)
        self.session_projector = SessionProjector(self.sessions)
        self.mode = "memory"

    def ingest(self, command: IngestEventCommand) -> IngestResult:
        if self.mode == "postgres" and self._pg_ingest is not None:
            return self._pg_ingest.ingest(command)
        assert self.ingest_service is not None
        assert self.session_projector is not None
        result = self.ingest_service.ingest(command)
        if result.created:
            envelope = self.store.get(EventId(result.event_id))
            if envelope is not None:
                domain_session = self.session_projector.apply(envelope)
                self.timeline.apply(
                    envelope, StoreOffset(result.store_offset), domain_session.id.value
                )
                self.memory.index_event(envelope)
        return result

    def replay(
        self, workspace_id: UUID, *, limit: int = 50, after_offset: int = 0
    ) -> list[TimelineItem]:
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                store = SqlAlchemyTimelineStore(session)
                return store.replay(
                    WorkspaceId(workspace_id), limit=limit, after_offset=after_offset
                )
            finally:
                session.close()
        return self.timeline.replay(
            WorkspaceId(workspace_id), limit=limit, after_offset=after_offset
        )

    def search(self, workspace_id: UUID, query: str, *, limit: int = 10) -> list[SearchHit]:
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                index = SqlAlchemyMemoryIndex(
                    session, embedder=self.embedder, use_pgvector=True
                )
                return index.search(query, workspace_id=workspace_id, limit=limit)
            finally:
                session.close()
        return self.memory.search(query, limit=limit)

    def issue_credential(
        self, *, workspace_id: UUID, actor_id: UUID, label: str = "default"
    ) -> IssuedCredential:
        issued = self.credential_service.issue(
            workspace_id=workspace_id, actor_id=actor_id, label=label
        )
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                SqlAlchemyCredentialStore(session, self.credential_service).save_issued(issued)
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            self.credentials.save_issued(issued)
        return issued

    def resolve_token(self, raw_token: str) -> Any | None:
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                return SqlAlchemyCredentialStore(
                    session, self.credential_service
                ).find_by_raw_token(raw_token)
            finally:
                session.close()
        return self.credentials.find_by_raw_token(raw_token, self.credential_service)

    def get_consent(self, workspace_id: UUID) -> ConsentPolicy:
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                return SqlAlchemyConsentStore(session).get(WorkspaceId(workspace_id))
            finally:
                session.close()
        return self.consent.get(WorkspaceId(workspace_id))

    def put_consent(self, workspace_id: UUID, categories: dict[str, bool]) -> ConsentPolicy:
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                store = SqlAlchemyConsentStore(session)
                policy = store.get(WorkspaceId(workspace_id))
                for name, enabled in categories.items():
                    policy.set_category(ConsentCategory(name), enabled)
                store.save(policy)
                session.commit()
                return policy
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        policy = self.consent.get(WorkspaceId(workspace_id))
        for name, enabled in categories.items():
            policy.set_category(ConsentCategory(name), enabled)
        self.consent.save(policy)
        return policy

    def process_outbox(self, limit: int = 50) -> int:
        if self._outbox_projector is None:
            return 0
        return self._outbox_projector.process_batch(limit=limit)

    def list_sessions(self, workspace_id: UUID) -> list[Any]:
        from chronicle_adapters.persistence.repositories import SqlAlchemySessionRepository
        from chronicle_domain.session.session import Session as DomainSession

        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                return SqlAlchemySessionRepository(session).list_for_workspace(
                    WorkspaceId(workspace_id)
                )
            finally:
                session.close()
        return self.sessions.list_for_workspace(WorkspaceId(workspace_id))

    def analytics_summary(
        self, workspace_id: UUID, from_time: datetime, to_time: datetime
    ) -> Any:
        from chronicle_application.analytics import summarize_sessions

        sessions = [
            s
            for s in self.list_sessions(workspace_id)
            if s.started_at >= from_time and s.started_at <= to_time
        ]
        items = self.replay(workspace_id, limit=5000, after_offset=0)
        window_items = [i for i in items if from_time <= i.occurred_at <= to_time]
        types = {i.type for i in window_items}
        return summarize_sessions(
            workspace_id=str(workspace_id),
            from_time=from_time,
            to_time=to_time,
            sessions=sessions,
            event_count=len(window_items),
            unique_types=len(types),
        )

    def sync_push(self, commands: list[IngestEventCommand]) -> Any:
        from uuid import uuid4

        from chronicle_application.ingest import IdempotencyConflictError
        from chronicle_application.sync import SyncConflict, SyncPushResult

        accepted: list[IngestResult] = []
        conflicts: list[SyncConflict] = []
        for command in commands:
            try:
                accepted.append(self.ingest(command))
            except IdempotencyConflictError:
                conflicts.append(
                    SyncConflict(conflict_id=uuid4(), idempotency_key=command.idempotency_key)
                )
        return SyncPushResult(accepted=accepted, conflicts=conflicts)

    def sync_pull(
        self, workspace_id: UUID, cursor: int, *, limit: int = 100
    ) -> tuple[list[Any], int]:
        if self.mode == "postgres" and self._session_factory is not None:
            from chronicle_adapters.persistence.event_store import SqlAlchemyEventStore

            session = self._session_factory()
            try:
                store = SqlAlchemyEventStore(session)
                rows = store.read_from(WorkspaceId(workspace_id), StoreOffset(cursor), limit)
                next_cursor = rows[-1][1].value if rows else cursor
                return rows, next_cursor
            finally:
                session.close()
        rows = self.store.read_from(WorkspaceId(workspace_id), StoreOffset(cursor), limit)
        next_cursor = rows[-1][1].value if rows else cursor
        return rows, next_cursor

    def readiness(self) -> dict[str, Any]:
        checks = {"mode": self.mode}
        if self.mode == "postgres" and self._session_factory is not None:
            session = self._session_factory()
            try:
                session.execute(__import__("sqlalchemy").text("SELECT 1"))
                checks["postgres"] = "ok"
                status = "ready"
            except Exception as exc:  # noqa: BLE001
                checks["postgres"] = f"error: {exc}"
                status = "not_ready"
            finally:
                session.close()
            return {"status": status, "checks": checks}
        checks["event_store"] = "ok"
        return {"status": "ready", "checks": checks}


_container: AppContainer | None = None


def get_container() -> AppContainer:
    global _container
    if _container is None:
        _container = AppContainer(settings=Settings.from_env())
        _container.configure()
    return _container


def reset_container_for_tests(*, auth_mode: str = "dev") -> AppContainer:
    global _container
    _container = AppContainer(settings=Settings(store_mode="memory", auth_mode=auth_mode))
    _container.configure()
    return _container
