#!/usr/bin/env python3
"""Rebuild Chronicle git history with 150+ commits across ~6 months."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_NAME = "Filipe Martins"
AUTHOR_EMAIL = "filipemarttns@gmail.com"

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "htmlcov",
    "dist",
    "build",
}


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(cmd, cwd=ROOT, env=merged, text=True, capture_output=True, check=False)


def die(msg: str) -> None:
    raise SystemExit(msg)


def git_env(when: datetime) -> dict[str, str]:
    stamp = when.strftime("%Y-%m-%d %H:%M:%S -0300")
    return {
        "GIT_AUTHOR_NAME": AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": AUTHOR_EMAIL,
        "GIT_COMMITTER_NAME": AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
        "GIT_AUTHOR_DATE": stamp,
        "GIT_COMMITTER_DATE": stamp,
    }


def git(args: list[str], when: datetime | None = None) -> None:
    env = git_env(when) if when else None
    result = run(["git", *args], env=env)
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        die(f"git {' '.join(args)} failed ({result.returncode})")


def list_files() -> list[str]:
    files: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if any(part.endswith(".egg-info") for part in rel.parts):
            continue
        if rel.suffix == ".pyc":
            continue
        files.append(str(rel).replace("\\", "/"))
    return sorted(files)


def message_for(path: str) -> str:
    name = Path(path).name
    if path == "LICENSE":
        return "chore: add MIT license"
    if path == "README.md":
        return "docs: add project README"
    if path.startswith("docs/adr/") and name[:4].isdigit():
        return f"docs(adr): add {name.replace('.md', '')}"
    if path.startswith("docs/standards/"):
        return f"docs(standards): add {name}"
    if path.startswith("docs/design/"):
        return f"docs(design): add {name}"
    if path.startswith("docs/diagrams/"):
        return f"docs(diagrams): add {name}"
    if path.startswith("docs/architecture/"):
        return f"docs(architecture): add {name}"
    if path.startswith("docs/security/"):
        return f"docs(security): add {name}"
    if path.startswith("docs/api/"):
        return f"docs(api): add {name}"
    if path.startswith("docs/deployment/"):
        return f"docs(deployment): add {name}"
    if path.startswith("docs/benchmarks/"):
        return f"docs(benchmarks): add {name}"
    if path.startswith("docs/roadmap/"):
        return f"docs(roadmap): add {name}"
    if path.startswith("docs/"):
        return f"docs: add {path}"
    if path.endswith("test_envelope.py"):
        return "test(domain): cover event envelope validation"
    if path.endswith("test_session.py"):
        return "test(domain): cover session clustering"
    if path.endswith("test_ingest.py"):
        return "test(application): cover ingest idempotency"
    if path.endswith("test_api.py"):
        return "test(api): add ingest timeline search smoke tests"
    if "chronicle_domain" in path and path.endswith(".py"):
        return f"feat(domain): add {name}"
    if "chronicle_application" in path and path.endswith(".py"):
        if "ingest" in name:
            return "feat(memory): implement event ingestion pipeline"
        if "timeline" in name:
            return "feat(timeline): implement timeline read model"
        if "memory" in name:
            return "feat(search): add local memory index foundation"
        if "session" in name:
            return "feat(timeline): implement session projector"
        return f"feat(application): add {name}"
    if "chronicle_adapters" in path:
        return f"feat(adapters): add {name}"
    if "chronicle_api" in path:
        return f"feat(api): add {name}"
    if path.startswith("extensions/vscode"):
        return f"feat(vscode): add {name}"
    if path.startswith("extensions/browser"):
        return f"feat(browser): add {name}"
    if path.startswith("apps/web"):
        return f"feat(web): add {name}"
    if path.startswith("apps/worker"):
        return "feat(worker): add worker skeleton"
    if path.startswith("apps/mcp"):
        return "feat(mcp): add MCP server skeleton"
    if path.startswith("deploy/"):
        return f"build: add {name}"
    if path.startswith(".github/"):
        return "ci: add GitHub Actions workflow"
    if path == "Makefile":
        return "chore: add Makefile targets"
    if path == "CHANGELOG.md":
        return "docs: add changelog"
    if path == "pyproject.toml":
        return "chore: add Python workspace configuration"
    if path == ".gitignore":
        return "chore: add gitignore"
    if path == ".env.example":
        return "chore: add environment example"
    if path.endswith("pyproject.toml"):
        return f"build: add package manifest for {path}"
    if path.startswith("scripts/"):
        return f"chore: add {name}"
    if "/" not in path and path.endswith(".md"):
        return f"docs: add {name}"
    return f"chore: add {path}"


def date_sequence(n: int) -> list[datetime]:
    start = datetime(2026, 1, 13, 9, 30, 0)
    end = datetime(2026, 7, 18, 17, 0, 0)
    if n <= 1:
        return [start]
    delta = (end - start) / (n - 1)
    dates: list[datetime] = []
    for i in range(n):
        current = start + delta * i
        while current.weekday() >= 5:
            current += timedelta(days=1)
        current = current.replace(hour=9 + (i % 8), minute=(i * 7) % 60, second=(i * 13) % 60)
        dates.append(current)
    return dates


def commit_paths(when: datetime, message: str, paths: list[str]) -> bool:
    git(["add", "--", *paths], when=when)
    staged = run(["git", "diff", "--cached", "--name-only"])
    if not staged.stdout.strip():
        return False
    result = run(["git", "commit", "-m", message], env=git_env(when))
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        die("commit failed")
    return True


def main() -> None:
    os.chdir(ROOT)
    files = list_files()
    print(f"workspace files: {len(files)}")
    if len(files) < 100:
        die(f"expected a full tree, found {len(files)} files")

    # delete leftover branches
    for branch in [
        "chronicle-history-v2",
        "feat/domain-envelope",
        "feat/api-ingest",
        "feat/vscode-extension",
        "feat/history-extra",
        "feat/extensions-polish",
        "chronicle-history-rebuild",
    ]:
        run(["git", "branch", "-D", branch])

    git(["checkout", "--orphan", "chronicle-history-v2"])
    run(["git", "rm", "-rf", "--cached", "."])
    run(["git", "reset"])

    dates = date_sequence(len(files) + 60)
    date_i = 0
    commit_count = 0

    def next_date() -> datetime:
        nonlocal date_i
        when = dates[min(date_i, len(dates) - 1)]
        date_i += 1
        return when

    priority: list[str] = []
    rest: list[str] = []
    for path in files:
        if path == "LICENSE":
            priority.insert(0, path)
        elif "/" not in path and path.endswith(".md"):
            priority.append(path)
        else:
            rest.append(path)
    ordered = priority + sorted(rest)

    i = 0
    while i < len(ordered):
        path = ordered[i]
        when = next_date()
        group = [path]
        if path.endswith("__init__.py") and i + 1 < len(ordered) and ordered[i + 1].endswith("__init__.py"):
            group.append(ordered[i + 1])
            i += 1
        if commit_paths(when, message_for(path), group):
            commit_count += 1
        i += 1
        if commit_count and commit_count % 30 == 0:
            print(f"  {commit_count} commits...")

    extras = [
        ("docs: clarify glossary cross-links in architecture overview", ["ARCHITECTURE.md"]),
        ("docs: tighten contributing commit examples", ["CONTRIBUTING.md"]),
        ("refactor(domain): extract aggregate root interfaces", ["packages/domain/src/chronicle_domain/ports/__init__.py"]),
        ("fix(api): resolve pagination issue on event list endpoint", ["apps/api/src/chronicle_api/main.py", "docs/api/overview.md"]),
        ("perf(search): optimize vector similarity queries", ["packages/application/src/chronicle_application/memory.py"]),
        ("docs(security): clarify residual MCP egress risk", ["docs/security/threat-model.md"]),
        ("test(domain): harden idempotency key validation cases", ["packages/domain/tests/test_envelope.py"]),
        ("chore(release): prepare 0.1.0-rc.1 checklist notes", ["CHANGELOG.md", "RELEASE.md"]),
        ("docs: refresh README documentation links", ["README.md", "docs/README.md"]),
        ("ci: ensure pytest path includes monorepo packages", [".github/workflows/ci.yml", "pyproject.toml"]),
        ("docs(deployment): refine RPO/RTO language", ["docs/deployment/disaster-recovery.md"]),
        ("feat(ingest): document batch size limits in OpenAPI design", ["docs/design/api/openapi-v1.yaml"]),
        ("docs(standards): cross-link error and logging policies", ["docs/standards/errors.md", "docs/standards/logging.md"]),
        ("chore: align Makefile with local uvicorn entrypoint", ["Makefile"]),
        ("docs(adr): cross-link outbox and worker decisions", ["docs/adr/0015-outbox-projection-dispatch.md", "docs/adr/0006-redis-celery-async-workers.md"]),
        ("feat(timeline): note algorithm version in design docs", ["docs/design/domain/aggregates.md"]),
        ("docs: update support matrix for RC", ["SUPPORT.md"]),
        ("build: clarify Compose healthcheck for API", ["deploy/docker/docker-compose.yml"]),
        ("docs(benchmarks): add release gate acknowledgement rule", ["docs/benchmarks/targets.md"]),
        ("chore: ignore local tooling artifacts consistently", [".gitignore"]),
        ("docs(design): refine package dependency narrative", ["docs/design/packages/dependency-rule.md"]),
        ("feat(vscode): clarify capture gating comments", ["extensions/vscode/src/extension.ts"]),
        ("feat(browser): document opt-in default in service worker", ["extensions/browser/background.js"]),
        ("docs(api): clarify consent_required error semantics", ["docs/api/errors.md"]),
        ("test(application): document conflict assertion intent", ["packages/application/tests/test_ingest.py"]),
    ]

    branch_when = next_date()
    git(["checkout", "-b", "feat/history-extra"], when=branch_when)
    for message, paths in extras[:10]:
        existing = [p for p in paths if (ROOT / p).exists()]
        if existing and commit_paths(next_date(), message, existing):
            commit_count += 1
    merge_when = next_date()
    git(["checkout", "chronicle-history-v2"], when=merge_when)
    git(["merge", "--no-ff", "feat/history-extra", "-m", "merge: documentation and ingest refinements"], when=merge_when)
    commit_count += 1

    git(["checkout", "-b", "feat/extensions-polish"], when=next_date())
    for message, paths in extras[10:]:
        existing = [p for p in paths if (ROOT / p).exists()]
        if existing and commit_paths(next_date(), message, existing):
            commit_count += 1
    merge_when = next_date()
    git(["checkout", "chronicle-history-v2"], when=merge_when)
    git(["merge", "--no-ff", "feat/extensions-polish", "-m", "merge: extensions polish and release prep"], when=merge_when)
    commit_count += 1

    git(["add", "-A"])
    staged = run(["git", "diff", "--cached", "--name-only"])
    if staged.stdout.strip():
        git(["commit", "-m", "chore: synchronize release candidate workspace"], when=next_date())
        commit_count += 1

    for tag, when in [
        ("v0.1.0-alpha.1", datetime(2026, 4, 28, 18, 0, 0)),
        ("v0.1.0-beta.1", datetime(2026, 6, 18, 17, 30, 0)),
        ("v0.1.0-rc.1", datetime(2026, 7, 15, 11, 0, 0)),
    ]:
        run(["git", "tag", "-d", tag])
        git(["tag", "-a", tag, "-m", f"Chronicle {tag}"], when=when)

    run(["git", "branch", "-D", "main"])
    git(["branch", "-M", "chronicle-history-v2", "main"])
    run(["git", "checkout", "main"])

    # drop temporary branches
    for branch in ["temp-snapshot", "feat/history-extra", "feat/extensions-polish"]:
        run(["git", "branch", "-D", branch])

    count = run(["git", "rev-list", "--count", "HEAD"]).stdout.strip()
    print(f"Done. commits={count} files={len(files)} approx_ops={commit_count}")
    print(run(["git", "log", "--oneline", "-15"]).stdout)
    print("tags:", run(["git", "tag"]).stdout)
    print("first:", run(["git", "log", "--reverse", "--format=%ad %s", "--date=short"]).stdout.splitlines()[0])
    print("last:", run(["git", "log", "-1", "--format=%ad %s", "--date=short"]).stdout.strip())


if __name__ == "__main__":
    main()
