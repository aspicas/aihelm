from __future__ import annotations

from pathlib import Path

import pytest

from aihelm.domain.models.workspace import Workspace
from aihelm.domain.ports.workspace_repository import WorkspaceRepository
from aihelm.services.workspace_service import WorkspaceService


class InMemoryWorkspaceRepository(WorkspaceRepository):
    def __init__(self) -> None:
        self._items: list[Workspace] = []

    def list_all(self) -> list[Workspace]:
        return sorted(self._items, key=lambda w: w.selected_at, reverse=True)

    def get_active(self) -> Workspace | None:
        return next((item for item in self._items if item.is_active), None)

    def upsert(self, workspace: Workspace) -> Workspace:
        for idx, item in enumerate(self._items):
            if item.path == workspace.path:
                persisted = Workspace(
                    id=item.id,
                    path=workspace.path,
                    name=workspace.name,
                    selected_at=workspace.selected_at,
                    is_active=workspace.is_active,
                )
                self._items[idx] = persisted
                return persisted
        self._items.append(workspace)
        return workspace

    def set_active(self, workspace_id: str) -> Workspace:
        active: Workspace | None = None
        for idx, item in enumerate(self._items):
            updated = Workspace(
                id=item.id,
                path=item.path,
                name=item.name,
                selected_at=item.selected_at,
                is_active=item.id == workspace_id,
            )
            self._items[idx] = updated
            if updated.is_active:
                active = updated
        if active is None:
            msg = f"Workspace not found: {workspace_id}"
            raise ValueError(msg)
        return active

    def remove(self, workspace_id: str) -> None:
        self._items = [item for item in self._items if item.id != workspace_id]


@pytest.fixture()
def repo() -> InMemoryWorkspaceRepository:
    return InMemoryWorkspaceRepository()


@pytest.fixture()
def service(repo: InMemoryWorkspaceRepository) -> WorkspaceService:
    return WorkspaceService(repo=repo)


class TestSelect:
    def test_select_sets_active(
        self, service: WorkspaceService, tmp_path: Path
    ) -> None:
        selected = service.select(tmp_path)
        active = service.get_active()
        assert active is not None
        assert selected.id == active.id
        assert active.path == tmp_path

    def test_select_switches_previous_active(
        self, service: WorkspaceService, tmp_path: Path
    ) -> None:
        path_a = tmp_path / "a"
        path_b = tmp_path / "b"
        path_a.mkdir()
        path_b.mkdir()
        first = service.select(path_a)
        second = service.select(path_b)
        active = service.get_active()
        assert first.id != second.id
        assert active is not None
        assert active.id == second.id


class TestGetActiveCwd:
    def test_returns_none_when_empty(self, service: WorkspaceService) -> None:
        assert service.get_active_cwd() is None

    def test_returns_selected_path(
        self, service: WorkspaceService, tmp_path: Path
    ) -> None:
        service.select(tmp_path)
        assert service.get_active_cwd() == tmp_path


class TestSubscriptions:
    def test_notifies_subscribers(
        self, service: WorkspaceService, tmp_path: Path
    ) -> None:
        captured: list[Workspace | None] = []

        def _subscriber(workspace: Workspace | None) -> None:
            captured.append(workspace)

        service.subscribe(_subscriber)
        service.select(tmp_path)

        assert len(captured) == 1
        first = captured[0]
        assert first is not None
        assert first.path == tmp_path
