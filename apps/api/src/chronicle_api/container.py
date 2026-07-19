"""Runtime dependency container for API and workers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from chronicle_adapters.memory import (
    InMemoryConsentPolicyStore,
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
    SqlAlchemyMemoryIndex,
    SqlAlchemyTimelineStore,
)
from chronicle_api.config import Settings
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
    store: InMemoryEventStore = field(default_factory=InMemoryEventStore)
    outbox: InMemoryOutbox = field(default_factory=InMemoryOutbox)
    consent: InMemoryConsentPolicyStore = field(default_factory=InMemoryConsentPolicyStore)
    sessions: InMemorySessionRepository = field(default_factory=InMemorySessionRepository)
    timeline: TimelineProjector = field(default_factory=TimelineProjector)
    memory: MemoryIndex = field(default_factory=MemoryIndex)
    ingest_service: IngestService | None = None
    session_projector: SessionProjector | None = None

    def configure(self) -> None:
        if self.settings.store_mode == "postgres":
            engine = create_db_engine(self.settings.database_url)
            create_all(engine)
            self._session_factory = create_session_factory(engine)
            self._pg_ingest = PostgresIngestGateway(
                self._session_factory, sync_project=self.settings.sync_project
            )
            self._outbox_projector = OutboxProjector(self._session_factory)
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
        self.timeline = TimelineProjector()
        self.memory = MemoryIndex()
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
                index = SqlAlchemyMemoryIndex(session)
                return index.search(query, workspace_id=workspace_id, limit=limit)
            finally:
                session.close()
        return self.memory.search(query, limit=limit)

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


def reset_container_for_tests() -> AppContainer:
    global _container
    _container = AppContainer(settings=Settings(store_mode="memory"))
    _container.configure()
    return _container
