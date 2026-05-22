"""Session clustering tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from chronicle_domain.session.session import Session, SessionClusteringService
from chronicle_domain.shared.ids import DeviceId, SessionId, WorkspaceId


def test_starts_when_no_open_session() -> None:
    service = SessionClusteringService()
    decision = service.decide(
        open_session=None,
        at=datetime.now(timezone.utc),
        workspace_id=WorkspaceId(uuid4()),
        device_id=DeviceId(uuid4()),
    )
    assert decision.action == "start"


def test_closes_on_idle_gap() -> None:
    ws = WorkspaceId(uuid4())
    device = DeviceId(uuid4())
    started = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)
    session = Session(
        id=SessionId(uuid4()),
        workspace_id=ws,
        device_id=device,
        started_at=started,
        last_activity_at=started,
    )
    service = SessionClusteringService(idle_timeout=timedelta(minutes=30))
    decision = service.decide(
        open_session=session,
        at=started + timedelta(minutes=45),
        workspace_id=ws,
        device_id=device,
    )
    assert decision.action == "close_and_start"
    assert decision.close_reason == "idle"
