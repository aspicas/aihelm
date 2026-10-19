"""Step implementations for workspace_selection.feature."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from aihelm.infra.persistence.json_workspace_repository import JsonWorkspaceRepository
from aihelm.services.workspace_service import WorkspaceService


@scenario(
    "../features/workspace_selection.feature", "Select a workspace that contains .git"
)
def test_select_workspace_with_git() -> None:
    pass


@scenario("../features/workspace_selection.feature", "Select a workspace without .git")
def test_select_workspace_without_git() -> None:
    pass


@scenario(
    "../features/workspace_selection.feature", "Workspace persists across restart"
)
def test_workspace_persists_across_restart() -> None:
    pass


@scenario(
    "../features/workspace_selection.feature",
    "Selecting a new workspace replaces active workspace",
)
def test_select_new_workspace_replaces_active() -> None:
    pass


@scenario(
    "../features/workspace_selection.feature",
    "Active workspace directory removed before restart",
)
def test_removed_active_workspace_on_restart() -> None:
    pass


@pytest.fixture()
def context() -> dict[str, object]:
    return {}


@given("an empty workspace repository", target_fixture="service")
def empty_workspace_repository(
    tmp_path: Path, context: dict[str, object]
) -> WorkspaceService:
    storage_path = tmp_path / "workspaces.json"
    context["storage_path"] = storage_path
    context["dirs"] = {}
    context["warning_required"] = False
    repo = JsonWorkspaceRepository(storage_path)
    return WorkspaceService(repo=repo)


@given(parsers.parse('a candidate directory "{name}" with .git'))
def candidate_directory_with_git(
    tmp_path: Path, context: dict[str, object], name: str
) -> None:
    workspace_path = tmp_path / name
    workspace_path.mkdir(parents=True, exist_ok=True)
    (workspace_path / ".git").mkdir(exist_ok=True)
    dirs = context["dirs"]
    assert isinstance(dirs, dict)
    dirs[name] = workspace_path


@given(parsers.parse('a candidate directory "{name}" without .git'))
def candidate_directory_without_git(
    tmp_path: Path, context: dict[str, object], name: str
) -> None:
    workspace_path = tmp_path / name
    workspace_path.mkdir(parents=True, exist_ok=True)
    dirs = context["dirs"]
    assert isinstance(dirs, dict)
    dirs[name] = workspace_path


@when("I select that directory as workspace")
def select_last_directory(
    service: WorkspaceService, context: dict[str, object]
) -> None:
    dirs = context["dirs"]
    assert isinstance(dirs, dict)
    selected_path = list(dirs.values())[-1]
    assert isinstance(selected_path, Path)
    workspace = service.select(selected_path)
    context["selected_path"] = selected_path
    context["warning_required"] = not workspace.has_git_dir()


@when(parsers.parse('I select "{name}" as workspace'))
def select_named_directory(
    service: WorkspaceService, context: dict[str, object], name: str
) -> None:
    dirs = context["dirs"]
    assert isinstance(dirs, dict)
    selected_path = dirs[name]
    assert isinstance(selected_path, Path)
    workspace = service.select(selected_path)
    context["selected_path"] = selected_path
    context["warning_required"] = not workspace.has_git_dir()


@when(parsers.parse('the directory "{name}" is removed'))
def remove_directory(context: dict[str, object], name: str) -> None:
    dirs = context["dirs"]
    assert isinstance(dirs, dict)
    workspace_path = dirs[name]
    assert isinstance(workspace_path, Path)
    shutil.rmtree(workspace_path)


@when("I restart workspace services from storage", target_fixture="service")
def restart_workspace_service(context: dict[str, object]) -> WorkspaceService:
    storage_path = context["storage_path"]
    assert isinstance(storage_path, Path)
    repo = JsonWorkspaceRepository(storage_path)
    return WorkspaceService(repo=repo)


@then("the active workspace path is that directory")
def active_workspace_matches_last(
    service: WorkspaceService, context: dict[str, object]
) -> None:
    selected_path = context["selected_path"]
    assert isinstance(selected_path, Path)
    assert service.get_active_cwd() == selected_path


@then(parsers.parse('the active workspace path is "{name}"'))
def active_workspace_matches_named(
    service: WorkspaceService, context: dict[str, object], name: str
) -> None:
    dirs = context["dirs"]
    assert isinstance(dirs, dict)
    selected_path = dirs[name]
    assert isinstance(selected_path, Path)
    assert service.get_active_cwd() == selected_path


@then("no git warning is required")
def no_git_warning_required(context: dict[str, object]) -> None:
    assert context["warning_required"] is False


@then("a git warning is required")
def git_warning_required(context: dict[str, object]) -> None:
    assert context["warning_required"] is True


@then("there is no active workspace")
def no_active_workspace(service: WorkspaceService) -> None:
    assert service.get_active() is None
    assert service.get_active_cwd() is None
