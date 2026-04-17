from __future__ import annotations

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.domain.ports.task_repository import TaskRepository


class TaskQueueService:
    """Orchestrates task creation and queue listing."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def add_task(self, name: str, prompt: str, branch_name: str) -> Task:
        """Create a new task and add it to the queue.

        Raises ValueError if branch_name is already used by an active task,
        or if any field fails validation.
        """
        active = self._repo.list_by_status(StatusEnum.QUEUED)
        active += self._repo.list_by_status(StatusEnum.RUNNING)
        if any(t.branch_name == branch_name for t in active):
            msg = f"Branch {branch_name!r} is already assigned to an active task"
            raise ValueError(msg)

        position = self._repo.next_position()
        task = Task(
            name=name,
            prompt=prompt,
            branch_name=branch_name,
            position=position,
        )
        self._repo.save(task)
        return task

    def list_queue(self) -> list[Task]:
        """Return all queued tasks ordered by position."""
        return self._repo.list_by_status(StatusEnum.QUEUED)

    def list_all_tasks(self) -> list[Task]:
        """Return all tasks regardless of status, ordered by position."""
        return self._repo.list_all()
