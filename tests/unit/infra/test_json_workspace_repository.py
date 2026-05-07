from __future__ import annotations

import json
from pathlib import Path

import pytest

from aihelm.domain.models.workspace import Workspace
from aihelm.infra.persistence.json_workspace_repository import JsonWorkspaceRepository


@pytest.fixture()
def repo(tmp_path: Path) -> JsonWorkspaceRepository:
    return JsonWorkspaceRepository(path=tmp_path / "workspaces.json")


class TestUpsertAndList:
    def test_roundtrip(self, repo: JsonWorkspaceRepository, tmp_path: Path) -> None:
        workspace = Workspace(path=tmp_path, is_active=True)
        persisted = repo.upsert(workspace)
        items = repo.list_all()
        assert len(items) == 1
        assert items[0].id == persisted.id
        assert items[0].path == tmp_path

    def test_upsert_same_path_keeps_single_record(
        self,
        repo: JsonWorkspaceRepository,
        tmp_path: Path,
    ) -> None:
        first = repo.upsert(Workspace(path=tmp_path, is_active=False))
        second = repo.upsert(Workspace(path=tmp_path, is_active=True))
        items = repo.list_all()
        assert len(items) == 1
        assert items[0].id == first.id
        assert second.id == first.id


class TestActiveWorkspace:
    def test_set_active_switches_previous(
        self, repo: JsonWorkspaceRepository, tmp_path: Path
    ) -> None:
        path_a = tmp_path / "a"
        path_b = tmp_path / "b"
        path_a.mkdir()
        path_b.mkdir()
        workspace_a = repo.upsert(Workspace(path=path_a))
        workspace_b = repo.upsert(Workspace(path=path_b))
        repo.set_active(workspace_a.id)
        active = repo.set_active(workspace_b.id)
        current = repo.get_active()
        assert active.id == workspace_b.id
        assert current is not None
        assert current.id == workspace_b.id

    def test_set_active_unknown_raises(self, repo: JsonWorkspaceRepository) -> None:
        with pytest.raises(ValueError, match="Workspace not found"):
            repo.set_active("missing")


class TestFileIntegrity:
    def test_missing_file_returns_empty(self, repo: JsonWorkspaceRepository) -> None:
        assert repo.list_all() == []
        assert repo.get_active() is None

    def test_json_is_valid(self, repo: JsonWorkspaceRepository, tmp_path: Path) -> None:
        repo.upsert(Workspace(path=tmp_path, is_active=False))
        raw = (tmp_path / "workspaces.json").read_text(encoding="utf-8")
        data = json.loads(raw)
        assert isinstance(data, list)
