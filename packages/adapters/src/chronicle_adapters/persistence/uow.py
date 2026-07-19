"""Unit of work and projection orchestration for SQLAlchemy sessions."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from chronicle_adapters.persistence.event_store import SqlAlchemyEventStore, SqlAlchemyOutbox
from chronicle_adapters.persistence.repositories import (
    SqlAlchemyConsentStore,
    SqlAlchemyMemoryIndex,
    SqlAlchemySessionRepository,
    SqlAlchemyTimelineStore,
)
from chronicle_application.ingest import IngestEventCommand, IngestResult, IngestService
from chronicle_application.session_projection import SessionProjector
from chronicle_domain.shared.ids import EventId, StoreOffset


@dataclass
class SqlAlchemyUnitOfWork:
    """Binds repositories to a single SQLAlchemy session/transaction."""

    session: Session

    def __post_init__(self) -> None:
        self.events = SqlAlchemyEventStore(self.session)
        self.outbox = SqlAlchemyOutbox(self.session)
        self.consent = SqlAlchemyConsentStore(self.session)
        self.sessions = SqlAlchemySessionRepository(self.session)
        self.timeline = SqlAlchemyTimelineStore(self.session)
        self.memory = SqlAlchemyMemoryIndex(self.session)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()


class PostgresIngestGateway:
    """Ingest through a short-lived unit of work, then optionally project."""

    def __init__(self, factory: sessionmaker[Session], *, sync_project: bool = True) -> None:
        self._factory = factory
        self._sync_project = sync_project

    def ingest(self, command: IngestEventCommand) -> IngestResult:
        session = self._factory()
        try:
            uow = SqlAlchemyUnitOfWork(session)
            service = IngestService(uow.events, uow.outbox, uow.consent)
            result = service.ingest(command)
            if self._sync_project and result.created:
                envelope = uow.events.get(EventId(result.event_id))
                if envelope is not None:
                    projector = SessionProjector(uow.sessions)
                    domain_session = projector.apply(envelope)
                    uow.timeline.apply(
                        envelope,
                        StoreOffset(result.store_offset),
                        domain_session.id.value,
                    )
                    uow.memory.index_event(envelope)
                    uow.outbox.mark_done_for_event(EventId(result.event_id))
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class OutboxProjector:
    """Drain pending outbox jobs into session/timeline/memory projections."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    def process_batch(self, limit: int = 50) -> int:
        session = self._factory()
        processed = 0
        try:
            uow = SqlAlchemyUnitOfWork(session)
            claimed = uow.outbox.claim_batch(limit=limit)
            for outbox_id, event_id, _job in claimed:
                try:
                    envelope = uow.events.get(EventId(event_id))
                    if envelope is None:
                        uow.outbox.mark_failed(outbox_id, "event missing")
                        continue
                    # Find offset via idempotency lookup
                    existing = uow.events.get_by_idempotency(
                        envelope.workspace_id, envelope.idempotency_key.value
                    )
                    if existing is None:
                        uow.outbox.mark_failed(outbox_id, "offset missing")
                        continue
                    _env, _fp, offset = existing
                    projector = SessionProjector(uow.sessions)
                    domain_session = projector.apply(envelope)
                    uow.timeline.apply(envelope, offset, domain_session.id.value)
                    uow.memory.index_event(envelope)
                    uow.outbox.mark_published(outbox_id)
                    processed += 1
                except Exception as exc:  # noqa: BLE001 - worker must continue batch
                    uow.outbox.mark_failed(outbox_id, str(exc))
            session.commit()
            return processed
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
