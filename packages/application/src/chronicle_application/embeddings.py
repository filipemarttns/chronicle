"""Deterministic local embeddings (stdlib only — safe for application layer)."""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"[a-z0-9_./-]+")


@dataclass(frozen=True, slots=True)
class HashingEmbedder:
    """Hashing trick embedder for CI and default local memory search."""

    dims: int = 384
    model_id: str = "hashing-v1"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dims
        tokens = _TOKEN_RE.findall(text.lower()) or ["empty"]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dims
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))
