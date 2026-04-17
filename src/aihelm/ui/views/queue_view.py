from __future__ import annotations

import flet as ft

from aihelm.services.task_queue_service import TaskQueueService
from aihelm.ui.components.task_card import TaskCard


class QueueView(ft.Column):
    """Left sidebar containing the task creation form and queue list."""

    def __init__(self, queue_service: TaskQueueService) -> None:
        super().__init__()
        self._queue_service = queue_service

        self._name_field = ft.TextField(
            label="Task Name",
            hint_text="e.g. Refactor auth module",
            dense=True,
        )
        self._prompt_field = ft.TextField(
            label="Prompt",
            hint_text="Instructions for the AI assistant...",
            multiline=True,
            min_lines=3,
            max_lines=6,
            dense=True,
        )
        self._branch_field = ft.TextField(
            label="Branch Name",
            hint_text="e.g. feature/refactor-auth",
            dense=True,
        )
        self._add_button = ft.Button(
            content=ft.Text("Add to Queue"),
            icon=ft.Icons.ADD,
            on_click=self._on_add_click,
            style=ft.ButtonStyle(
                bgcolor="#0d6efd",
                color="#ffffff",
            ),
        )
        self._error_text = ft.Text(
            value="",
            color="#dc3545",
            size=12,
            visible=False,
        )
        self._task_list = ft.ListView(
            spacing=8,
            expand=True,
        )

        self.spacing = 0
        self.expand = True
        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "New Task",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        self._name_field,
                        self._prompt_field,
                        self._branch_field,
                        self._error_text,
                        self._add_button,
                    ],
                    spacing=10,
                ),
                padding=16,
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Queue",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        self._task_list,
                    ],
                    spacing=8,
                    expand=True,
                ),
                padding=16,
                expand=True,
            ),
        ]

    def did_mount(self) -> None:
        self._load_queue()

    def _load_queue(self) -> None:
        tasks = self._queue_service.list_all_tasks()
        self._task_list.controls = [TaskCard(t) for t in tasks]
        self._task_list.update()

    def _on_add_click(self, _e: ft.Event[ft.Button]) -> None:
        name = (self._name_field.value or "").strip()
        prompt = (self._prompt_field.value or "").strip()
        branch = (self._branch_field.value or "").strip()

        self._error_text.visible = False
        self._error_text.update()

        try:
            task = self._queue_service.add_task(name, prompt, branch)
        except ValueError as exc:
            self._error_text.value = str(exc)
            self._error_text.visible = True
            self._error_text.update()
            return

        self._task_list.controls.append(TaskCard(task))
        self._task_list.update()

        self._name_field.value = ""
        self._prompt_field.value = ""
        self._branch_field.value = ""
        self._name_field.update()
        self._prompt_field.update()
        self._branch_field.update()
