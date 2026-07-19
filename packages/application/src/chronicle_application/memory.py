"""Local memory index with hashing embeddings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID

from chronicle_application.embeddings import HashingEmbedder, cosine_similarity
from chronicle_domain.capture.envelope import EventEnvelope


@dataclass(frozen=True, slots=True)
class SearchHit:
    chunk_id: UUID
    score: float
    snippet: str
    citations: tuple[UUID, ...]


def event_text(envelope: EventEnvelope) -> str:
    return (
        f"{envelope.type.value} "
        + " ".join(f"{k}={v}" for k, v in envelope.payload.items() if isinstance(v, (str, int)))
    ).lower()


@dataclass
class MemoryIndex:
    embedder: HashingEmbedder = field(default_factory=HashingEmbedder)
    _chunks: list[tuple[UUID, str, tuple[UUID, ...], list[float]]] = field(default_factory=list)

    def index_event(self, envelope: EventEnvelope) -> None:
        text = event_text(envelope)
        vector = self.embedder.embed(text)
        self._chunks.append(
            (envelope.event_id.value, text, (envelope.event_id.value,), vector)
        )

    def search(self, query: str, *, limit: int = 10) -> list[SearchHit]:
        import re

        if not self._chunks:
            return []

        def tokens(text: str) -> set[str]:
            return {t for t in re.split(r"[^a-z0-9_.]+", text.lower()) if t}

        query_vec = self.embedder.embed(query.lower())
        query_tokens = tokens(query)
        scored: list[SearchHit] = []
        for chunk_id, text, citations, vector in self._chunks:
            cosine = cosine_similarity(query_vec, vector)
            overlap = (
                len(query_tokens.intersection(tokens(text))) / max(len(query_tokens), 1)
                if query_tokens
                else 0.0
            )
            score = max(cosine, overlap)
            if score <= 0:
                continue
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
