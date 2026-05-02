from __future__ import annotations

from pathlib import Path

import pytest

from aihelm.domain.models.workspace import Workspace


class TestWorkspaceValidation:
    def test_rejects_non_directory_path(self, tmp_path: Path) -> None:
        file_path = tmp_path / "file.txt"
        file_path.write_text("x", encoding="utf-8")
        with pytest.raises(ValueError, match="existing directory"):
            Workspace(path=file_path)

    def test_defaults_name_to_directory_name(self, tmp_path: Path) -> None:
        workspace = Workspace(path=tmp_path)
        assert workspace.name == tmp_path.name


class TestWorkspaceGitDetection:
    def test_has_git_dir_true(self, tmp_path: Path) -> None:
        (tmp_path / ".git").mkdir()
        workspace = Workspace(path=tmp_path)
        assert workspace.has_git_dir() is True

    def test_has_git_dir_false(self, tmp_path: Path) -> None:
        workspace = Workspace(path=tmp_path)
        assert workspace.has_git_dir() is False
