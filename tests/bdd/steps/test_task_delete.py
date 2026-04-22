"""Step implementations for task_delete.feature."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from tests.conftest import InMemoryTaskRepository

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.infra.persistence.json_task_repository import JsonTaskRepository
from aihelm.services.task_queue_service import TaskQueueService

# --- Scenarios ---


@scenario("../features/task_delete.feature", "Delete a queued task")
def test_delete_queued_task() -> None:
    pass


@scenario("../features/task_delete.feature", "Reject deleting a running task")
def test_reject_delete_running() -> None:
    pass


@scenario("../features/task_delete.feature", "Deleted task releases branch for reuse")
def test_branch_reuse_after_delete() -> None:
    pass


@scenario("../features/task_delete.feature", "Deletion persists across restarts")
def test_delete_persists() -> None:
    pass


# --- Fixtures ---


@pytest.fixture()
def context() -> dict[str, object]:
    return {}


# --- Given steps ---


@given("an empty task queue", target_fixture="service")
def empty_queue() -> TaskQueueService:
    return TaskQueueService(repo=InMemoryTaskRepository())


@given(
    parsers.parse(
        'a running task with name "{name}" prompt "{prompt}" and branch "{branch}"'
    ),
    target_fixture="last_task",
)
def running_task(
    service: TaskQueueService, name: str, prompt: str, branch: str
) -> Task:
    task = Task(
        name=name,
        prompt=prompt,
        branch_name=branch,
        status=StatusEnum.RUNNING,
        position=0,
    )
    service._repo.save(task)
    return task


@given("a JSON-backed task queue", target_fixture="service")
def json_backed_queue(tmp_path: Path, context: dict[str, object]) -> TaskQueueService:
    path = tmp_path / "tasks.json"
    context["json_path"] = path
    repo = JsonTaskRepository(path=path)
    return TaskQueueService(repo=repo)


# --- When steps ---


@when(
    parsers.parse(
        'I add a task with name "{name}" prompt "{prompt}" and branch "{branch}"'
    ),
    target_fixture="last_task",
)
def add_task(service: TaskQueueService, name: str, prompt: str, branch: str) -> Task:
    return service.add_task(name, prompt, branch)


@when("I delete the task")
def delete_task(service: TaskQueueService, last_task: Task) -> None:
    service.delete_task(last_task.id)


@when("I try to delete the task", target_fixture="error")
def try_delete_task(service: TaskQueueService, last_task: Task) -> ValueError | None:
    try:
        service.delete_task(last_task.id)
    except ValueError as exc:
        return exc
    return None


@when("I reload the queue from storage", target_fixture="service")
def reload_queue(context: dict[str, object]) -> TaskQueueService:
    path: Path = context["json_path"]  # type: ignore[assignment]
    repo = JsonTaskRepository(path=path)
    return TaskQueueService(repo=repo)


# --- Then steps ---


@then(parsers.parse("the queue contains {count:d} task"))
@then(parsers.parse("the queue contains {count:d} tasks"))
def queue_has_count(service: TaskQueueService, count: int) -> None:
    assert len(service.list_all_tasks()) == count


@then(parsers.parse('the task has name "{name}"'))
def task_has_name(service: TaskQueueService, name: str) -> None:
    tasks = service.list_all_tasks()
    assert any(t.name == name for t in tasks)


@then(parsers.parse('I receive a validation error containing "{text}"'))
def got_validation_error(error: ValueError | None, text: str) -> None:
    assert error is not None
    assert text in str(error)
