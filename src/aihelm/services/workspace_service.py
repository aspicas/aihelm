from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from aihelm.domain.models.workspace import Workspace
from aihelm.domain.ports.workspace_repository import WorkspaceRepository


class WorkspaceService:
    """Orchestrates workspace selection and retrieval of active cwd."""

    def __init__(self, repo: WorkspaceRepository) -> None:
        self._repo = repo
        self._subscribers: list[Callable[[Workspace | None], None]] = []

    def select(self, path: Path) -> Workspace:
        workspace = Workspace(path=path.resolve(), is_active=True)
        persisted = self._repo.upsert(workspace)
        active = self._repo.set_active(persisted.id)
        self._notify(active)
        return active

    def get_active(self) -> Workspace | None:
        return self._repo.get_active()

    def get_active_cwd(self) -> Path | None:
        active = self.get_active()
        if active is None:
            return None
        return active.path

    def list_all(self) -> list[Workspace]:
        return self._repo.list_all()

    def subscribe(self, callback: Callable[[Workspace | None], None]) -> None:
        self._subscribers.append(callback)

    def _notify(self, workspace: Workspace | None) -> None:
        for callback in self._subscribers:
            callback(workspace)
