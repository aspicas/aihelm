from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class Workspace:
    """A project root that AIHelm can use as execution cwd."""

    path: Path
    name: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    selected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = False

    def __post_init__(self) -> None:
        if not self.path.is_dir():
            msg = f"Workspace path must be an existing directory: {self.path}"
            raise ValueError(msg)
        if not self.name:
            object.__setattr__(self, "name", self.path.name or str(self.path))

    def has_git_dir(self) -> bool:
        return (self.path / ".git").is_dir()
