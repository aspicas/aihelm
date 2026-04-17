from __future__ import annotations

from pathlib import Path

import flet as ft

from aihelm.infra.persistence import JsonTaskRepository
from aihelm.services import TaskQueueService
from aihelm.ui.views import QueueView

_DEFAULT_DATA_DIR = Path.home() / ".aihelm"
_TASKS_FILE = _DEFAULT_DATA_DIR / "tasks.json"


def main(page: ft.Page) -> None:
    page.title = "AIHelm"
    page.window.width = 1200
    page.window.height = 800
    page.bgcolor = "#121212"
    page.theme_mode = ft.ThemeMode.DARK

    repo = JsonTaskRepository(path=_TASKS_FILE)
    queue_service = TaskQueueService(repo=repo)
    queue_view = QueueView(queue_service=queue_service)

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    content=queue_view,
                    width=380,
                    bgcolor="#1a1a1a",
                    border=ft.border.only(right=ft.BorderSide(1, "#333333")),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "AIHelm",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#666666",
                            ),
                            ft.Text(
                                "Select a task to begin execution.",
                                color="#555555",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            expand=True,
        ),
    )


if __name__ == "__main__":
    ft.app(target=main)  # type: ignore[no-untyped-call]
