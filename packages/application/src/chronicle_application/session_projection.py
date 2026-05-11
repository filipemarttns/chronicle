"""Session projection from ingested events."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from chronicle_domain.capture.envelope import EventEnvelope
from chronicle_domain.ports import SessionRepositoryPort
from chronicle_domain.session.session import Session, SessionClusteringService
from chronicle_domain.shared.ids import SessionId


class SessionProjector:
    """Assign events to sessions using deterministic clustering."""

    def __init__(
        self,
        sessions: SessionRepositoryPort,
        clustering: SessionClusteringService | None = None,
    ) -> None:
        self._sessions = sessions
        self._clustering = clustering or SessionClusteringService()

    def apply(self, envelope: EventEnvelope) -> Session:
        open_session = self._sessions.find_open(envelope.workspace_id, envelope.device_id)
        decision = self._clustering.decide(
            open_session=open_session,
            at=envelope.occurred_at,
            workspace_id=envelope.workspace_id,
            device_id=envelope.device_id,
        )
        if decision.action == "touch" and open_session is not None:
            open_session.touch(envelope.occurred_at)
            self._sessions.save(open_session)
            return open_session

        if decision.action == "close_and_start" and open_session is not None:
            open_session.close(envelope.occurred_at, reason=decision.close_reason or "idle")
            self._sessions.save(open_session)

        session = Session(
            id=SessionId(uuid4()),
            workspace_id=envelope.workspace_id,
            device_id=envelope.device_id,
            started_at=envelope.occurred_at,
            last_activity_at=envelope.occurred_at,
        )
        self._sessions.save(session)
        return session
