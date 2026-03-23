# Versioning Strategy (Design)

Unifies HTTP, event, package, and MCP versioning for implementers. See also ADR-0016, [RELEASE.md](../../../RELEASE.md), and [api/versioning.md](../../api/versioning.md).

## Layers

| Layer | Scheme | Breaking change means |
| --- | --- | --- |
| HTTP API | `/vN` URL major | Remove/rename fields; change semantics; auth behavior break |
| Event payload | `schema_version` per `type` | Rename/remove/change meaning of payload fields |
| Domain events | same as events | Same rules |
| MCP tools | tool schema version field / tool rename | Rename tool; remove required args; change meaning |
| Python packages | semver when published; path imports in monorepo until then | Public function/type removal |
| JS packages | semver via package.json | Export removal |
| Projector logic | `projector_version` string | Incompatible read-model shape → rebuild |
| Session algorithm | `algorithm_version` | Idle/clustering rule change → new sessions only or rebuild |

## Compatibility matrix (targets)

| Producer | Consumer | Rule |
| --- | --- | --- |
| Extension N | API N | Same release train preferred |
| Extension N-1 | API N | Must work for at least one minor during 0.x; 90 days after 1.0 |
| API N | DB migrated from N-1 | Alembic upgrade path required |
| Worker N | Events from N-1 schemas | Dual-read window |

## Deprecation process

1. Mark in OpenAPI / schema `deprecated`
2. Changelog entry
3. Metrics for deprecated endpoint usage when available
4. Remove only on major (post-1.0) after window

## Design doc versioning

`docs/design/api/openapi-v1.yaml` `info.version` uses `*-design` until the first implemented RC tags `0.x.y`. After that, generated OpenAPI from code becomes source of truth and this file is either generated or replaced by export.
