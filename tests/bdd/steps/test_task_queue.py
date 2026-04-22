"""Step implementations for task_queue.feature."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from tests.conftest import InMemoryTaskRepository

from aihelm.domain.models.task import Task
from aihelm.infra.persistence.json_task_repository import JsonTaskRepository
from aihelm.services.task_queue_service import TaskQueueService

# --- Scenarios ---


@scenario("../features/task_queue.feature", "Add a valid task to the queue")
def test_add_valid_task() -> None:
    pass


@scenario("../features/task_queue.feature", "Reject task with invalid branch name")
def test_reject_invalid_branch() -> None:
    pass


@scenario("../features/task_queue.feature", "Reject task with empty name")
def test_reject_empty_name() -> None:
    pass


@scenario("../features/task_queue.feature", "Reject duplicate active branch")
def test_reject_duplicate_branch() -> None:
    pass


@scenario("../features/task_queue.feature", "Tasks are ordered by position")
def test_task_ordering() -> None:
    pass


@scenario("../features/task_queue.feature", "Tasks persist across restarts")
def test_persistence() -> None:
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
    parsers.parse('a queued task with branch "{branch}"'),
    target_fixture="service",
)
def queue_with_existing_task(
    service: TaskQueueService, branch: str
) -> TaskQueueService:
    service.add_task("Existing", "p", branch)
    return service


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


@when(
    parsers.parse(
        'I try to add a task with name "{name}" prompt "{prompt}" and branch "{branch}"'
    ),
    target_fixture="error",
)
def try_add_task(
    service: TaskQueueService, name: str, prompt: str, branch: str
) -> ValueError | None:
    try:
        service.add_task(name, prompt, branch)
    except ValueError as exc:
        return exc
    return None


@when("I try to add a task with an empty name", target_fixture="error")
def try_add_task_empty_name(service: TaskQueueService) -> ValueError | None:
    try:
        service.add_task("", "something", "feature/ok")
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
    assert len(service.list_queue()) == count


@then(parsers.parse('the task has status "{status}"'))
def task_has_status(last_task: Task, status: str) -> None:
    assert last_task.status == status


@then(parsers.parse('the task has branch "{branch}"'))
def task_has_branch(last_task: Task, branch: str) -> None:
    assert last_task.branch_name == branch


@then(parsers.parse('the task has name "{name}"'))
def task_has_name(service: TaskQueueService, name: str) -> None:
    tasks = service.list_queue()
    assert any(t.name == name for t in tasks)


@then(parsers.parse('I receive a validation error containing "{text}"'))
def got_validation_error(error: ValueError | None, text: str) -> None:
    assert error is not None
    assert text in str(error)


@then(parsers.parse('the queue lists "{first}" before "{second}"'))
def queue_order(service: TaskQueueService, first: str, second: str) -> None:
    tasks = service.list_queue()
    names = [t.name for t in tasks]
    assert names.index(first) < names.index(second)
