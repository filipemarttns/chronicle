"""Session aggregate and deterministic clustering rules (ADR-0011)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from chronicle_domain.shared.ids import (
    DeviceId,
    DomainValidationError,
    InvariantViolation,
    SessionId,
    WorkspaceId,
)

DEFAULT_IDLE_TIMEOUT = timedelta(minutes=30)
ALGORITHM_VERSION = "v1"


@dataclass
class Session:
    """Time-bounded unit of engineering work for a workspace device."""

    id: SessionId
    workspace_id: WorkspaceId
    device_id: DeviceId
    started_at: datetime
    last_activity_at: datetime
    algorithm_version: str = ALGORITHM_VERSION
    ended_at: datetime | None = None

    @property
    def is_open(self) -> bool:
        return self.ended_at is None

    def touch(self, at: datetime) -> None:
        if not self.is_open:
            raise InvariantViolation("cannot touch a closed session")
        if at < self.last_activity_at:
            raise DomainValidationError("activity time before last_activity_at")
        self.last_activity_at = at

    def close(self, at: datetime, *, reason: str) -> str:
        if not self.is_open:
            raise InvariantViolation("session already closed")
        if at < self.started_at:
            raise DomainValidationError("end before start")
        self.ended_at = at
        return reason


@dataclass(frozen=True, slots=True)
class ClusteringDecision:
    action: str  # start | touch | close_and_start
    close_reason: str | None = None


class SessionClusteringService:
    """Pure clustering decisions for session reconstruction."""

    def __init__(self, idle_timeout: timedelta = DEFAULT_IDLE_TIMEOUT) -> None:
        self._idle_timeout = idle_timeout

    def decide(
        self,
        *,
        open_session: Session | None,
        at: datetime,
        workspace_id: WorkspaceId,
        device_id: DeviceId,
    ) -> ClusteringDecision:
        if open_session is None:
            return ClusteringDecision(action="start")
        if (
            open_session.workspace_id != workspace_id
            or open_session.device_id != device_id
        ):
            return ClusteringDecision(action="close_and_start", close_reason="workspace_switch")
        gap = at - open_session.last_activity_at
        if gap > self._idle_timeout:
            return ClusteringDecision(action="close_and_start", close_reason="idle")
        return ClusteringDecision(action="touch")
