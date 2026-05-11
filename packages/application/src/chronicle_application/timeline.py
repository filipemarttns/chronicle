"""Timeline read-model helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from chronicle_domain.capture.envelope import EventEnvelope
from chronicle_domain.shared.ids import StoreOffset, WorkspaceId


@dataclass(frozen=True, slots=True)
class TimelineItem:
    event_id: UUID
    type: str
    occurred_at: datetime
    source: str
    store_offset: int
    session_id: UUID | None = None
    summary: str = ""
    payload_preview: dict[str, Any] | None = None


class TimelineProjector:
    """Maintain an ordered in-memory timeline for a workspace."""

    def __init__(self) -> None:
        self._items: dict[str, list[TimelineItem]] = {}

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
        key = str(envelope.workspace_id)
        self._items.setdefault(key, []).append(item)
        self._items[key].sort(key=lambda i: (i.occurred_at, i.store_offset))
        return item

    def replay(
        self,
        workspace_id: WorkspaceId,
        *,
        limit: int = 50,
        after_offset: int = 0,
    ) -> list[TimelineItem]:
        items = [
            item
            for item in self._items.get(str(workspace_id), [])
            if item.store_offset > after_offset
        ]
        return items[:limit]
