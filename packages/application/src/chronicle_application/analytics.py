"""Developer analytics summaries derived from sessions and timeline activity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from chronicle_domain.session.session import Session


@dataclass(frozen=True, slots=True)
class AnalyticsSummary:
    workspace_id: str
    from_time: datetime
    to_time: datetime
    metrics: dict[str, float]


def summarize_sessions(
    *,
    workspace_id: str,
    from_time: datetime,
    to_time: datetime,
    sessions: Iterable[Session],
    event_count: int,
    unique_types: int,
) -> AnalyticsSummary:
    sessions = list(sessions)
    open_count = sum(1 for s in sessions if s.is_open)
    closed = [s for s in sessions if s.ended_at is not None]
    durations = []
    for session in closed:
        assert session.ended_at is not None
        durations.append((session.ended_at - session.started_at).total_seconds())
    avg_duration = sum(durations) / len(durations) if durations else 0.0
    focus_minutes = sum(durations) / 60.0
    return AnalyticsSummary(
        workspace_id=workspace_id,
        from_time=from_time,
        to_time=to_time,
        metrics={
            "session_count": float(len(sessions)),
            "open_sessions": float(open_count),
            "avg_session_seconds": avg_duration,
            "focus_minutes": focus_minutes,
            "event_count": float(event_count),
            "unique_event_types": float(unique_types),
            "events_per_hour": _events_per_hour(event_count, from_time, to_time),
        },
    )


def _events_per_hour(event_count: int, from_time: datetime, to_time: datetime) -> float:
    span = max((to_time - from_time).total_seconds(), 1.0)
    return event_count / (span / 3600.0)


def default_range(to_time: datetime | None = None) -> tuple[datetime, datetime]:
    end = to_time or datetime.utcnow().replace(tzinfo=None)
    # Callers should pass timezone-aware values; this helper is a fallback.
    return end - timedelta(days=7), end
