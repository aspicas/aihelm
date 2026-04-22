"""Step implementations for task_edit.feature."""

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


@scenario("../features/task_edit.feature", "Edit the name of a queued task")
def test_edit_name() -> None:
    pass


@scenario("../features/task_edit.feature", "Edit the prompt of a queued task")
def test_edit_prompt() -> None:
    pass


@scenario("../features/task_edit.feature", "Edit the branch of a queued task")
def test_edit_branch() -> None:
    pass


@scenario("../features/task_edit.feature", "Reject editing a running task")
def test_reject_edit_running() -> None:
    pass


@scenario("../features/task_edit.feature", "Reject duplicate branch on edit")
def test_reject_duplicate_branch_edit() -> None:
    pass


@scenario("../features/task_edit.feature", "Edited task persists")
def test_edit_persists() -> None:
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


@when(
    parsers.parse('I edit the task name to "{name}"'),
    target_fixture="last_task",
)
def edit_task_name(service: TaskQueueService, last_task: Task, name: str) -> Task:
    return service.update_task(
        last_task.id,
        name=name,
        prompt=last_task.prompt,
        branch_name=last_task.branch_name,
    )


@when(
    parsers.parse('I edit the task prompt to "{prompt}"'),
    target_fixture="last_task",
)
def edit_task_prompt(service: TaskQueueService, last_task: Task, prompt: str) -> Task:
    return service.update_task(
        last_task.id,
        name=last_task.name,
        prompt=prompt,
        branch_name=last_task.branch_name,
    )


@when(
    parsers.parse('I edit the task branch to "{branch}"'),
    target_fixture="last_task",
)
def edit_task_branch(service: TaskQueueService, last_task: Task, branch: str) -> Task:
    return service.update_task(
        last_task.id,
        name=last_task.name,
        prompt=last_task.prompt,
        branch_name=branch,
    )


@when(
    parsers.parse('I try to edit the task name to "{name}"'),
    target_fixture="error",
)
def try_edit_task_name(
    service: TaskQueueService, last_task: Task, name: str
) -> ValueError | None:
    try:
        service.update_task(
            last_task.id,
            name=name,
            prompt=last_task.prompt,
            branch_name=last_task.branch_name,
        )
    except ValueError as exc:
        return exc
    return None


@when(
    parsers.parse('I try to edit task "{task_name}" branch to "{branch}"'),
    target_fixture="error",
)
def try_edit_task_branch(
    service: TaskQueueService, task_name: str, branch: str
) -> ValueError | None:
    tasks = service.list_all_tasks()
    target = next(t for t in tasks if t.name == task_name)
    try:
        service.update_task(
            target.id,
            name=target.name,
            prompt=target.prompt,
            branch_name=branch,
        )
    except ValueError as exc:
        return exc
    return None


@when("I reload the queue from storage", target_fixture="service")
def reload_queue(context: dict[str, object]) -> TaskQueueService:
    path: Path = context["json_path"]  # type: ignore[assignment]
    repo = JsonTaskRepository(path=path)
    return TaskQueueService(repo=repo)


# --- Then steps ---


@then(parsers.parse('the task has name "{name}"'))
def task_has_name(service: TaskQueueService, name: str) -> None:
    tasks = service.list_all_tasks()
    assert any(t.name == name for t in tasks)


@then(parsers.parse('the task prompt is "{prompt}"'))
def task_has_prompt(last_task: Task, prompt: str) -> None:
    assert last_task.prompt == prompt


@then(parsers.parse('the task has branch "{branch}"'))
def task_has_branch(last_task: Task, branch: str) -> None:
    assert last_task.branch_name == branch


@then(parsers.parse('I receive a validation error containing "{text}"'))
def got_validation_error(error: ValueError | None, text: str) -> None:
    assert error is not None
    assert text in str(error)
