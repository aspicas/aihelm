from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import flet as ft

from aihelm.domain.models.task import Task
from aihelm.infra.persistence import JsonTaskRepository, JsonWorkspaceRepository
from aihelm.services import TaskQueueService, WorkspaceService
from aihelm.ui.views import QueueView, TaskDetailView

_DEFAULT_DATA_DIR = Path.home() / ".aihelm"
_TASKS_FILE = _DEFAULT_DATA_DIR / "tasks.json"
_WORKSPACES_FILE = _DEFAULT_DATA_DIR / "workspaces.json"


@dataclass
class AppRuntimeState:
    """Shared runtime state used by execution backends."""

    workspace_cwd: Path | None = None


_APP_STATE = AppRuntimeState()


def get_active_workspace_cwd() -> Path | None:
    """Return active workspace cwd for process execution modules."""
    return _APP_STATE.workspace_cwd


def main(page: ft.Page) -> None:
    page.title = "AIHelm"
    page.window.width = 1200
    page.window.height = 800
    page.bgcolor = "#121212"
    page.theme_mode = ft.ThemeMode.DARK

    repo = JsonTaskRepository(path=_TASKS_FILE)
    queue_service = TaskQueueService(repo=repo)
    workspace_repo = JsonWorkspaceRepository(path=_WORKSPACES_FILE)
    workspace_service = WorkspaceService(repo=workspace_repo)
    _APP_STATE.workspace_cwd = workspace_service.get_active_cwd()

    def _sync_runtime_state() -> None:
        _APP_STATE.workspace_cwd = workspace_service.get_active_cwd()

    def _show_git_warning() -> None:
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(
                    "Warning: No .git directory found. "
                    "Version control features may not work."
                ),
                bgcolor="#8a5a00",
            ),
        )

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    async def _open_workspace_picker() -> None:
        selected_path = await file_picker.get_directory_path(
            dialog_title="Select Project Directory",
        )
        if not selected_path:
            return
        try:
            selected = workspace_service.select(Path(selected_path))
        except ValueError:
            return
        _sync_runtime_state()
        if not selected.has_git_dir():
            _show_git_warning()

    detail_view = TaskDetailView(
        queue_service=queue_service,
        on_task_updated=lambda _task: queue_view.refresh_list(),
        on_task_deleted=lambda: queue_view.refresh_list(),
    )

    def _on_task_selected(task: Task) -> None:
        detail_view.show_task(task)

    queue_view = QueueView(
        queue_service=queue_service,
        workspace_service=workspace_service,
        on_select_project=_open_workspace_picker,
        on_task_selected=_on_task_selected,
    )

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    content=queue_view,
                    width=380,
                    bgcolor="#1a1a1a",
                    border=ft.Border.only(right=ft.BorderSide(1, "#333333")),
                ),
                ft.Container(
                    content=detail_view,
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


if __name__ == "__main__":
    ft.run(main)
