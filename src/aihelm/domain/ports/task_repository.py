from __future__ import annotations

from abc import ABC, abstractmethod

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task


class TaskRepository(ABC):
    """Port for persisting and retrieving tasks."""

    @abstractmethod
    def save(self, task: Task) -> None: ...

    @abstractmethod
    def get(self, task_id: str) -> Task | None: ...

    @abstractmethod
    def list_by_status(self, status: StatusEnum) -> list[Task]: ...

    @abstractmethod
    def list_all(self) -> list[Task]: ...

    @abstractmethod
    def delete(self, task_id: str) -> None: ...

    @abstractmethod
    def next_position(self) -> int: ...
