# Secret Redaction

Implements ADR-0021.

## Where redaction runs

1. **Ingest API** (mandatory) before append
2. **Export / MCP response** (mandatory) before leave-host serialization
3. **Clients** (best-effort) before send

## Detector categories

| Category | Examples |
| --- | --- |
| Bearer tokens | `Authorization: Bearer ...` |
| PEM key blocks | `BEGIN RSA PRIVATE KEY` |
| Cloud API keys | common vendor prefixes |
| Password flags | `--password`, `-p` with values |
| URL credentials | `https://user:pass@host` |
| JWT-shaped strings | three base64url segments |

Matches replace with typed placeholders to aid debugging (`[REDACTED:bearer]`).

## Metadata

```json
{
  "redaction_meta": {
    "counts": { "bearer": 1, "url_credential": 0 },
    "detector_version": "1.4.0"
  }
}
```

## False positives

Detectors may redact benign strings. Workspace allowlist configuration is a later enhancement; until then, prefer narrower capture or shorter command logging.

## Testing

Corpus of positive/negative samples lives under test fixtures (synthetic only). Detector version bumps require expanding the corpus.
