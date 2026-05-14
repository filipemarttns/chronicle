"""Secret redaction helpers applied before event append."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


_BEARER = re.compile(r"(?i)(bearer\s+)[a-z0-9\-._~+/]+=*")
_URL_CREDS = re.compile(r"(://)([^:/@]+):([^@/]+)(@)")
_PEM = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.DOTALL,
)
_JWT = re.compile(r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b")


@dataclass(frozen=True, slots=True)
class RedactionResult:
    value: Any
    counts: dict[str, int]


class SecretRedactionService:
    """Best-effort secret redaction for strings and nested payloads."""

    DETECTOR_VERSION = "1.0.0"

    def redact_string(self, text: str) -> RedactionResult:
        counts: dict[str, int] = {}
        out = text

        def sub(pattern: re.Pattern[str], placeholder: str, key: str, value: str) -> str:
            nonlocal counts
            replaced, n = pattern.subn(placeholder, value)
            if n:
                counts[key] = counts.get(key, 0) + n
            return replaced

        out = sub(_PEM, "[REDACTED:pem]", "pem", out)
        out = sub(_BEARER, r"\1[REDACTED:bearer]", "bearer", out)
        out = sub(_URL_CREDS, r"\1[REDACTED:user]:[REDACTED:pass]\4", "url_credential", out)
        out = sub(_JWT, "[REDACTED:jwt]", "jwt", out)
        return RedactionResult(value=out, counts=counts)

    def redact_payload(self, payload: dict[str, Any]) -> RedactionResult:
        totals: dict[str, int] = {}

        def walk(node: Any) -> Any:
            if isinstance(node, str):
                result = self.redact_string(node)
                for key, count in result.counts.items():
                    totals[key] = totals.get(key, 0) + count
                return result.value
            if isinstance(node, list):
                return [walk(item) for item in node]
            if isinstance(node, dict):
                return {key: walk(value) for key, value in node.items()}
            return node

        return RedactionResult(value=walk(payload), counts=totals)
