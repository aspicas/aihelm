"""Shared test fixtures including InMemoryTaskRepository."""

from __future__ import annotations

import pytest

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.domain.ports.task_repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """In-memory fake for testing (no I/O)."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_by_status(self, status: StatusEnum) -> list[Task]:
        return sorted(
            (t for t in self._tasks.values() if t.status == status),
            key=lambda t: t.position,
        )

    def list_all(self) -> list[Task]:
        return sorted(self._tasks.values(), key=lambda t: t.position)

    def delete(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)

    def next_position(self) -> int:
        if not self._tasks:
            return 0
        return max(t.position for t in self._tasks.values()) + 1


@pytest.fixture()
def in_memory_repo() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()
