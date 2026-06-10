"""Naive local memory index for semantic-ish search (token overlap).

Production uses pgvector embeddings; this provides a deterministic local
fallback for tests and early milestones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID

from chronicle_domain.capture.envelope import EventEnvelope


@dataclass(frozen=True, slots=True)
class SearchHit:
    chunk_id: UUID
    score: float
    snippet: str
    citations: tuple[UUID, ...]


@dataclass
class MemoryIndex:
    _chunks: list[tuple[UUID, str, tuple[UUID, ...]]] = field(default_factory=list)

    def index_event(self, envelope: EventEnvelope) -> None:
        text = f"{envelope.type.value} " + " ".join(
            f"{k}={v}" for k, v in envelope.payload.items() if isinstance(v, (str, int))
        )
        self._chunks.append((envelope.event_id.value, text.lower(), (envelope.event_id.value,)))

    def search(self, query: str, *, limit: int = 10) -> list[SearchHit]:
        import re

        def tokens(text: str) -> set[str]:
            return {t for t in re.split(r"[^a-z0-9_.]+", text.lower()) if t}

        query_tokens = tokens(query)
        scored: list[SearchHit] = []
        for chunk_id, text, citations in self._chunks:
            overlap = query_tokens.intersection(tokens(text))
            if not overlap:
                continue
            score = len(overlap) / max(len(query_tokens), 1)
            scored.append(
                SearchHit(
                    chunk_id=chunk_id,
                    score=score,
                    snippet=text[:200],
                    citations=citations,
                )
            )
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:limit]

    def extend(self, envelopes: Iterable[EventEnvelope]) -> None:
        for envelope in envelopes:
            self.index_event(envelope)


