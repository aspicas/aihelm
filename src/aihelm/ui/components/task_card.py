from __future__ import annotations

from collections.abc import Callable

import flet as ft

from aihelm.domain.models.task import Task
from aihelm.ui.components.status_badge import StatusBadge


class TaskCard(ft.Container):
    """Card displaying a single task's summary."""

    def __init__(
        self,
        task: Task,
        on_click: Callable[[Task], None] | None = None,
    ) -> None:
        self.task = task
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                task.name,
                                weight=ft.FontWeight.W_600,
                                size=14,
                                expand=True,
                                no_wrap=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            StatusBadge(task.status),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        task.branch_name,
                        size=12,
                        color="#888888",
                        font_family="monospace",
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        task.created_at.strftime("%Y-%m-%d %H:%M"),
                        size=11,
                        color="#aaaaaa",
                    ),
                ],
                spacing=4,
            ),
            padding=12,
            border=ft.border.all(1, "#333333"),
            border_radius=8,
            bgcolor="#1e1e1e",
            ink=True,
            on_click=lambda _e: on_click(task) if on_click else None,
        )
