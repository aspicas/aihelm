from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.domain.ports.task_repository import TaskRepository


def _task_to_dict(task: Task) -> dict[str, Any]:
    return {
        "id": task.id,
        "name": task.name,
        "prompt": task.prompt,
        "branch_name": task.branch_name,
        "status": str(task.status),
        "created_at": task.created_at.isoformat(),
        "position": task.position,
    }


def _dict_to_task(data: dict[str, Any]) -> Task:
    return Task(
        id=data["id"],
        name=data["name"],
        prompt=data["prompt"],
        branch_name=data["branch_name"],
        status=StatusEnum(data["status"]),
        created_at=datetime.fromisoformat(data["created_at"]).replace(
            tzinfo=UTC,
        ),
        position=data["position"],
    )


class JsonTaskRepository(TaskRepository):
    """TaskRepository backed by a JSON file with atomic writes."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()

    def _read_all(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        raw = self._path.read_text(encoding="utf-8")
        result: list[dict[str, Any]] = json.loads(raw)
        return result

    def _write_all(self, tasks: list[dict[str, Any]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(tasks, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(self._path)

    def save(self, task: Task) -> None:
        with self._lock:
            items = self._read_all()
            for i, item in enumerate(items):
                if item["id"] == task.id:
                    items[i] = _task_to_dict(task)
                    break
            else:
                items.append(_task_to_dict(task))
            self._write_all(items)

    def get(self, task_id: str) -> Task | None:
        with self._lock:
            for item in self._read_all():
                if item["id"] == task_id:
                    return _dict_to_task(item)
        return None

    def list_by_status(self, status: StatusEnum) -> list[Task]:
        with self._lock:
            items = self._read_all()
        return sorted(
            (_dict_to_task(i) for i in items if i["status"] == str(status)),
            key=lambda t: t.position,
        )

    def list_all(self) -> list[Task]:
        with self._lock:
            items = self._read_all()
        return sorted(
            (_dict_to_task(i) for i in items),
            key=lambda t: t.position,
        )

    def delete(self, task_id: str) -> None:
        with self._lock:
            items = [i for i in self._read_all() if i["id"] != task_id]
            self._write_all(items)

    def next_position(self) -> int:
        with self._lock:
            items = self._read_all()
        if not items:
            return 0
        max_pos: int = max(i["position"] for i in items)
        return max_pos + 1
