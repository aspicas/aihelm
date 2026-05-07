from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable

import flet as ft

from aihelm.domain.models.workspace import Workspace
from aihelm.services.workspace_service import WorkspaceService
from aihelm.ui._runtime import is_mounted

PickHandler = Callable[[], None] | Callable[[], Awaitable[None]]


class WorkspaceSelector(ft.Column):
    """UI block to select and show the active project workspace."""

    def __init__(
        self,
        workspace_service: WorkspaceService,
        on_pick: PickHandler,
    ) -> None:
        super().__init__()
        self._workspace_service = workspace_service
        self._on_pick = on_pick
        self._path_text = ft.Text(value="", size=12, selectable=True)

        self.controls = [
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text("Select Project"),
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self._handle_pick_click,
                    ),
                ],
            ),
            self._path_text,
        ]
        self.spacing = 6

        self._workspace_service.subscribe(self._on_workspace_changed)
        self._render(self._workspace_service.get_active())

    async def _handle_pick_click(self, _e: ft.Event[ft.Button]) -> None:
        result = self._on_pick()
        if inspect.isawaitable(result):
            await result

    def _on_workspace_changed(self, workspace: Workspace | None) -> None:
        self._render(workspace)

    def _render(self, workspace: Workspace | None) -> None:
        if workspace is None:
            self._path_text.value = "No project selected"
            self._path_text.color = "#aaaaaa"
            self.tooltip = None
        else:
            has_git = workspace.has_git_dir()
            self._path_text.value = str(workspace.path)
            self._path_text.color = "#cccccc" if has_git else "#f59e0b"
            self.tooltip = (
                None
                if has_git
                else (
                    "Warning: No .git directory found. "
                    "Version control features may not work."
                )
            )
        if is_mounted(self):
            self.update()
