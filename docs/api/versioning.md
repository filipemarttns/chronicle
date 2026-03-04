# API Versioning

Companion to ADR-0016 and [RELEASE.md](../../RELEASE.md).

## URL majors

- `/v1` — current development major
- Future breaking changes → `/v2`

## Compatibility rules within a major

Allowed without major bump:

- New optional fields on requests/responses
- New endpoints
- New event types
- New error codes (clients must tolerate unknown codes)

Breaking:

- Removing/renaming fields
- Changing field meaning
- Tightening validation that rejects previously valid clients
- Changing auth scheme semantics without negotiation

## Deprecation

1. Mark in OpenAPI (`deprecated: true`)
2. Announce in changelog
3. Minimum window after `1.0.0`: 90 days before removal in next major

## Event schemas vs HTTP

Event `schema_version` can advance without HTTP major changes if payloads remain additive for existing types. Coordinated release notes required when both move.
