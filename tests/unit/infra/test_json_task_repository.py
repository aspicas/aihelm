import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.infra.persistence.json_task_repository import JsonTaskRepository


def _make_task(
    *,
    name: str = "Test",
    prompt: str = "Do it",
    branch: str = "feature/test",
    position: int = 0,
    status: StatusEnum = StatusEnum.QUEUED,
    task_id: str = "test-id",
) -> Task:
    return Task(
        name=name,
        prompt=prompt,
        branch_name=branch,
        id=task_id,
        status=status,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        position=position,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> JsonTaskRepository:
    return JsonTaskRepository(path=tmp_path / "tasks.json")


class TestSaveAndGet:
    def test_roundtrip(self, repo: JsonTaskRepository) -> None:
        task = _make_task()
        repo.save(task)
        got = repo.get(task.id)
        assert got is not None
        assert got.id == task.id
        assert got.name == task.name
        assert got.prompt == task.prompt
        assert got.branch_name == task.branch_name
        assert got.status == task.status
        assert got.position == task.position

    def test_upsert_replaces(self, repo: JsonTaskRepository) -> None:
        task = _make_task()
        repo.save(task)
        updated = Task(
            name="Updated",
            prompt=task.prompt,
            branch_name=task.branch_name,
            id=task.id,
            status=StatusEnum.RUNNING,
            created_at=task.created_at,
            position=task.position,
        )
        repo.save(updated)
        got = repo.get(task.id)
        assert got is not None
        assert got.name == "Updated"
        assert got.status == StatusEnum.RUNNING


class TestListAll:
    def test_sorted_by_position(self, repo: JsonTaskRepository) -> None:
        repo.save(_make_task(position=2, task_id="b", branch="feature/b"))
        repo.save(_make_task(position=0, task_id="a", branch="feature/a"))
        repo.save(_make_task(position=1, task_id="c", branch="feature/c"))
        tasks = repo.list_all()
        assert [t.position for t in tasks] == [0, 1, 2]

    def test_empty_repo(self, repo: JsonTaskRepository) -> None:
        assert repo.list_all() == []


class TestListByStatus:
    def test_filters_correctly(self, repo: JsonTaskRepository) -> None:
        repo.save(_make_task(task_id="a", branch="feature/a", status=StatusEnum.QUEUED))
        repo.save(
            _make_task(task_id="b", branch="feature/b", status=StatusEnum.RUNNING),
        )
        queued = repo.list_by_status(StatusEnum.QUEUED)
        assert len(queued) == 1
        assert queued[0].id == "a"


class TestDelete:
    def test_removes_task(self, repo: JsonTaskRepository) -> None:
        task = _make_task()
        repo.save(task)
        repo.delete(task.id)
        assert repo.get(task.id) is None

    def test_nonexistent_is_noop(self, repo: JsonTaskRepository) -> None:
        repo.delete("does-not-exist")  # should not raise


class TestNextPosition:
    def test_empty_returns_zero(self, repo: JsonTaskRepository) -> None:
        assert repo.next_position() == 0

    def test_after_saves(self, repo: JsonTaskRepository) -> None:
        repo.save(_make_task(position=3, task_id="a", branch="feature/a"))
        repo.save(_make_task(position=7, task_id="b", branch="feature/b"))
        assert repo.next_position() == 8


class TestFileIntegrity:
    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        deep = tmp_path / "a" / "b" / "tasks.json"
        repo = JsonTaskRepository(path=deep)
        repo.save(_make_task())
        assert deep.exists()

    def test_json_is_valid(self, repo: JsonTaskRepository, tmp_path: Path) -> None:
        repo.save(_make_task())
        raw = (tmp_path / "tasks.json").read_text(encoding="utf-8")
        data = json.loads(raw)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_missing_file_returns_empty(self, repo: JsonTaskRepository) -> None:
        assert repo.list_all() == []
        assert repo.get("x") is None
