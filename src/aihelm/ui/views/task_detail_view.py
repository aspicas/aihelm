from __future__ import annotations

from collections.abc import Callable

import flet as ft

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.services.task_queue_service import TaskQueueService
from aihelm.ui.components.status_badge import StatusBadge


class TaskDetailView(ft.Column):
    """Right panel showing task details with edit capability."""

    def __init__(
        self,
        queue_service: TaskQueueService,
        on_task_updated: Callable[[Task], None] | None = None,
        on_task_deleted: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._queue_service = queue_service
        self._on_task_updated = on_task_updated
        self._on_task_deleted = on_task_deleted
        self._current_task: Task | None = None
        self._editing = False

        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self._show_empty_state()

    def show_task(self, task: Task) -> None:
        """Display a task in view mode."""
        self._current_task = task
        self._editing = False
        self._build_view_mode()
        self.update()

    def _show_empty_state(self) -> None:
        self.controls = [
            ft.Text(
                "AIHelm",
                size=24,
                weight=ft.FontWeight.BOLD,
                color="#666666",
            ),
            ft.Text(
                "Select a task to view details.",
                color="#555555",
            ),
        ]

    def _build_view_mode(self) -> None:
        task = self._current_task
        if task is None:
            self._show_empty_state()
            return

        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START

        header_row = ft.Row(
            controls=[
                ft.Text(
                    task.name,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
                StatusBadge(task.status),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        actions: list[ft.Control] = []
        if task.status == StatusEnum.QUEUED:
            actions.append(
                ft.Button(
                    content=ft.Text("Edit"),
                    icon=ft.Icons.EDIT,
                    on_click=self._on_edit_click,
                    style=ft.ButtonStyle(
                        bgcolor="#0d6efd",
                        color="#ffffff",
                    ),
                ),
            )
        if task.status != StatusEnum.RUNNING:
            actions.append(
                ft.Button(
                    content=ft.Text("Delete"),
                    icon=ft.Icons.DELETE,
                    on_click=self._on_delete_click,
                    style=ft.ButtonStyle(
                        bgcolor="#dc3545",
                        color="#ffffff",
                    ),
                ),
            )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        header_row,
                        ft.Divider(height=1),
                        self._field_row("ID", task.id),
                        self._field_row(
                            "Created",
                            task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        self._field_row("Branch", task.branch_name, monospace=True),
                        ft.Divider(height=1),
                        ft.Text(
                            "Prompt",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="#aaaaaa",
                        ),
                        ft.Container(
                            content=ft.Text(
                                task.prompt,
                                size=14,
                                color="#cccccc",
                            ),
                            bgcolor="#1e1e1e",
                            border=ft.border.all(1, "#333333"),
                            border_radius=8,
                            padding=12,
                        ),
                        ft.Row(controls=actions) if actions else ft.Container(),
                    ],
                    spacing=12,
                ),
                padding=24,
                expand=True,
            ),
        ]

    def _build_edit_mode(self) -> None:
        task = self._current_task
        if task is None:
            return

        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START

        self._edit_name = ft.TextField(
            label="Task Name",
            value=task.name,
            dense=True,
        )
        self._edit_prompt = ft.TextField(
            label="Prompt",
            value=task.prompt,
            multiline=True,
            min_lines=3,
            max_lines=10,
            dense=True,
        )
        self._edit_branch = ft.TextField(
            label="Branch Name",
            value=task.branch_name,
            dense=True,
        )
        self._edit_error = ft.Text(
            value="",
            color="#dc3545",
            size=12,
            visible=False,
        )

        header_row = ft.Row(
            controls=[
                ft.Text(
                    "Editing Task",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
                StatusBadge(task.status),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        header_row,
                        ft.Divider(height=1),
                        self._field_row("ID", task.id),
                        self._field_row(
                            "Created",
                            task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        ft.Divider(height=1),
                        self._edit_name,
                        self._edit_prompt,
                        self._edit_branch,
                        self._edit_error,
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content=ft.Text("Save"),
                                    icon=ft.Icons.SAVE,
                                    on_click=self._on_save_click,
                                    style=ft.ButtonStyle(
                                        bgcolor="#198754",
                                        color="#ffffff",
                                    ),
                                ),
                                ft.Button(
                                    content=ft.Text("Cancel"),
                                    icon=ft.Icons.CANCEL,
                                    on_click=self._on_cancel_click,
                                    style=ft.ButtonStyle(
                                        bgcolor="#6c757d",
                                        color="#ffffff",
                                    ),
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=12,
                ),
                padding=24,
                expand=True,
            ),
        ]

    @staticmethod
    def _field_row(
        label: str,
        value: str,
        *,
        monospace: bool = False,
    ) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Text(
                    label,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="#aaaaaa",
                    width=80,
                ),
                ft.Text(
                    value,
                    size=14,
                    color="#cccccc",
                    font_family="monospace" if monospace else None,
                    expand=True,
                    no_wrap=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def _on_edit_click(self, _e: ft.Event[ft.Button]) -> None:
        self._editing = True
        self._build_edit_mode()
        self.update()

    def _on_cancel_click(self, _e: ft.Event[ft.Button]) -> None:
        self._editing = False
        self._build_view_mode()
        self.update()

    def _on_save_click(self, _e: ft.Event[ft.Button]) -> None:
        if self._current_task is None:
            return

        name = (self._edit_name.value or "").strip()
        prompt = (self._edit_prompt.value or "").strip()
        branch = (self._edit_branch.value or "").strip()

        self._edit_error.visible = False
        self._edit_error.update()

        try:
            updated = self._queue_service.update_task(
                self._current_task.id,
                name=name,
                prompt=prompt,
                branch_name=branch,
            )
        except ValueError as exc:
            self._edit_error.value = str(exc)
            self._edit_error.visible = True
            self._edit_error.update()
            return

        self._current_task = updated
        self._editing = False
        self._build_view_mode()
        self.update()

        if self._on_task_updated:
            self._on_task_updated(updated)

    def _on_delete_click(self, _e: ft.Event[ft.Button]) -> None:
        if self._current_task is None or self.page is None:
            return

        self._delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Task"),
            content=ft.Text(
                f'Are you sure you want to delete "{self._current_task.name}"?'
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self._close_delete_dialog,
                ),
                ft.TextButton(
                    "Delete",
                    on_click=self._confirm_delete,
                    style=ft.ButtonStyle(color="#dc3545"),
                ),
            ],
        )
        self.page.overlay.append(self._delete_dialog)
        self._delete_dialog.open = True
        self.page.update()

    def _close_delete_dialog(self, _e: ft.Event[ft.TextButton]) -> None:
        if self.page is None:
            return
        self._delete_dialog.open = False
        self.page.update()

    def _confirm_delete(self, _e: ft.Event[ft.TextButton]) -> None:
        if self._current_task is None or self.page is None:
            return

        self._delete_dialog.open = False
        self.page.update()

        try:
            self._queue_service.delete_task(self._current_task.id)
        except ValueError:
            return

        self._current_task = None
        self._editing = False
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self._show_empty_state()
        self.update()

        if self._on_task_deleted:
            self._on_task_deleted()
