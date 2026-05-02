from __future__ import annotations

from abc import ABC, abstractmethod

from aihelm.domain.models.workspace import Workspace


class WorkspaceRepository(ABC):
    """Port for persisting and retrieving workspaces."""

    @abstractmethod
    def list_all(self) -> list[Workspace]: ...

    @abstractmethod
    def get_active(self) -> Workspace | None: ...

    @abstractmethod
    def upsert(self, workspace: Workspace) -> Workspace: ...

    @abstractmethod
    def set_active(self, workspace_id: str) -> Workspace: ...

    @abstractmethod
    def remove(self, workspace_id: str) -> None: ...
