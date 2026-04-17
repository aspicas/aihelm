from __future__ import annotations

import flet as ft

from aihelm.domain.models.status import StatusEnum

_STATUS_COLORS: dict[StatusEnum, str] = {
    StatusEnum.QUEUED: "#6c757d",
    StatusEnum.RUNNING: "#0d6efd",
    StatusEnum.PAUSED: "#ffc107",
    StatusEnum.DONE: "#198754",
    StatusEnum.FAILED: "#dc3545",
}

_STATUS_TEXT_COLORS: dict[StatusEnum, str] = {
    StatusEnum.QUEUED: "#ffffff",
    StatusEnum.RUNNING: "#ffffff",
    StatusEnum.PAUSED: "#000000",
    StatusEnum.DONE: "#ffffff",
    StatusEnum.FAILED: "#ffffff",
}


class StatusBadge(ft.Container):
    """Colored pill badge showing a task's status."""

    def __init__(self, status: StatusEnum) -> None:
        super().__init__(
            content=ft.Text(
                status.value.upper(),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=_STATUS_TEXT_COLORS.get(status, "#ffffff"),
            ),
            bgcolor=_STATUS_COLORS.get(status, "#6c757d"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
        )
