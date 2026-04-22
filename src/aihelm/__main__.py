from __future__ import annotations

from pathlib import Path

import flet as ft

from aihelm.domain.models.task import Task
from aihelm.infra.persistence import JsonTaskRepository
from aihelm.services import TaskQueueService
from aihelm.ui.views import QueueView, TaskDetailView

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

    detail_view = TaskDetailView(
        queue_service=queue_service,
        on_task_updated=lambda _task: queue_view.refresh_list(),
        on_task_deleted=lambda: queue_view.refresh_list(),
    )

    def _on_task_selected(task: Task) -> None:
        detail_view.show_task(task)

    queue_view = QueueView(
        queue_service=queue_service,
        on_task_selected=_on_task_selected,
    )

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
                    content=detail_view,
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


if __name__ == "__main__":
    ft.app(target=main)  # type: ignore[no-untyped-call]
