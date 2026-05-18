"""Consent categories and evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from chronicle_domain.capture.envelope import EventType
from chronicle_domain.shared.ids import ConsentDenied, DomainValidationError, WorkspaceId


class ConsentCategory(StrEnum):
    EDITOR = "editor"
    TERMINAL = "terminal"
    GIT = "git"
    BROWSER = "browser"
    ASSISTANT = "assistant"
    BUILD = "build"


_TYPE_PREFIX_TO_CATEGORY: dict[str, ConsentCategory] = {
    "editor.": ConsentCategory.EDITOR,
    "terminal.": ConsentCategory.TERMINAL,
    "git.": ConsentCategory.GIT,
    "vcs.": ConsentCategory.GIT,
    "browser.": ConsentCategory.BROWSER,
    "assistant.": ConsentCategory.ASSISTANT,
    "build.": ConsentCategory.BUILD,
    "test.": ConsentCategory.BUILD,
    "stacktrace.": ConsentCategory.BUILD,
    "file.": ConsentCategory.EDITOR,
}


def category_for_event_type(event_type: EventType) -> ConsentCategory | None:
    """Map telemetry type to consent category; domain/system types return None."""

    value = event_type.value
    if value.startswith("domain.") or value.startswith("system.") or value == "session.marker":
        return None
    for prefix, category in _TYPE_PREFIX_TO_CATEGORY.items():
        if value.startswith(prefix):
            return category
    raise DomainValidationError(f"no consent mapping for event type: {value}")


@dataclass
class ConsentPolicy:
    """Per-workspace consent flags."""

    workspace_id: WorkspaceId
    categories: dict[ConsentCategory, bool] = field(
        default_factory=lambda: {
            ConsentCategory.EDITOR: False,
            ConsentCategory.TERMINAL: False,
            ConsentCategory.GIT: False,
            ConsentCategory.BROWSER: False,
            ConsentCategory.ASSISTANT: False,
            ConsentCategory.BUILD: False,
        }
    )

    def allow(self, event_type: EventType) -> None:
        category = category_for_event_type(event_type)
        if category is None:
            return
        if not self.categories.get(category, False):
            raise ConsentDenied(f"consent required for category {category.value}")

    def set_category(self, category: ConsentCategory, enabled: bool) -> None:
        self.categories[category] = enabled
