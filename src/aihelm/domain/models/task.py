from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from aihelm.domain.models.status import StatusEnum

# Compiled regex for git-check-ref-format validation.
# Rejects: control chars, space, ~^:?*[\, double-dot, @{, leading/trailing dot,
# .lock suffix, leading dash, trailing slash, consecutive slashes, bare "@".
_BRANCH_NAME_RE = re.compile(
    r"^(?!\.)"  # no leading dot
    r"(?!.*\.\.)"  # no double-dot anywhere
    r"(?!.*@\{)"  # no @{ anywhere
    r"(?!.*/\.)"  # no slash-dot (component starting with dot)
    r"(?!.*//)"  # no consecutive slashes
    r"(?!-)"  # no leading dash
    r"[^\x00-\x1f\x7f ~^:?*\[\\]+"  # valid characters only
    r"(?<!\.lock)"  # no .lock suffix
    r"(?<!\.)"  # no trailing dot
    r"(?<!/)$"  # no trailing slash
)

_BARE_AT = re.compile(r"^@$")


@dataclass(frozen=True)
class Task:
    """A unit of work to be executed by an AI code assistant."""

    name: str
    prompt: str
    branch_name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: StatusEnum = StatusEnum.QUEUED
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )
    position: int = 0

    def __post_init__(self) -> None:
        if not self.name or len(self.name) > 200:
            msg = "Task name must be between 1 and 200 characters"
            raise ValueError(msg)
        if not self.prompt:
            msg = "Prompt must not be empty"
            raise ValueError(msg)
        if _BARE_AT.match(self.branch_name) or not _BRANCH_NAME_RE.match(
            self.branch_name,
        ):
            msg = f"Invalid git branch name: {self.branch_name!r}"
            raise ValueError(msg)
