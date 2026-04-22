from __future__ import annotations

import dataclasses

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

    def update_task(
        self,
        task_id: str,
        *,
        name: str,
        prompt: str,
        branch_name: str,
    ) -> Task:
        """Edit a queued task's name, prompt, and branch_name.

        Raises ValueError if the task is not found, is not queued,
        the new branch conflicts with another active task, or any
        field fails validation.
        """
        existing = self._repo.get(task_id)
        if existing is None:
            msg = "Task not found"
            raise ValueError(msg)

        if existing.status != StatusEnum.QUEUED:
            msg = "Only queued tasks can be edited"
            raise ValueError(msg)

        if branch_name != existing.branch_name:
            active = self._repo.list_by_status(StatusEnum.QUEUED)
            active += self._repo.list_by_status(StatusEnum.RUNNING)
            if any(t.branch_name == branch_name and t.id != task_id for t in active):
                msg = f"Branch {branch_name!r} is already assigned to an active task"
                raise ValueError(msg)

        updated = dataclasses.replace(
            existing,
            name=name,
            prompt=prompt,
            branch_name=branch_name,
        )
        self._repo.save(updated)
        return updated

    def delete_task(self, task_id: str) -> None:
        """Delete a task from the queue.

        Raises ValueError if the task is not found or is currently running.
        """
        existing = self._repo.get(task_id)
        if existing is None:
            msg = "Task not found"
            raise ValueError(msg)

        if existing.status == StatusEnum.RUNNING:
            msg = "Cannot delete a running task"
            raise ValueError(msg)

        self._repo.delete(task_id)

    def list_queue(self) -> list[Task]:
        """Return all queued tasks ordered by position."""
        return self._repo.list_by_status(StatusEnum.QUEUED)

    def list_all_tasks(self) -> list[Task]:
        """Return all tasks regardless of status, ordered by position."""
        return self._repo.list_all()
