import pytest
from tests.conftest import InMemoryTaskRepository

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task
from aihelm.services.task_queue_service import TaskQueueService


@pytest.fixture()
def repo() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture()
def service(repo: InMemoryTaskRepository) -> TaskQueueService:
    return TaskQueueService(repo=repo)


class TestAddTask:
    def test_returns_queued_task(self, service: TaskQueueService) -> None:
        task = service.add_task("Fix bug", "Fix it", "feature/fix")
        assert task.status == StatusEnum.QUEUED
        assert task.name == "Fix bug"

    def test_auto_assigns_position(self, service: TaskQueueService) -> None:
        t1 = service.add_task("First", "p1", "feature/first")
        t2 = service.add_task("Second", "p2", "feature/second")
        assert t1.position == 0
        assert t2.position == 1

    def test_rejects_duplicate_active_branch(self, service: TaskQueueService) -> None:
        service.add_task("First", "p", "feature/dup")
        with pytest.raises(ValueError, match="already assigned"):
            service.add_task("Second", "p", "feature/dup")

    def test_allows_branch_reuse_after_done(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        done_task = Task(
            name="Old",
            prompt="p",
            branch_name="feature/reuse",
            status=StatusEnum.DONE,
            position=0,
        )
        repo.save(done_task)
        task = service.add_task("New", "p", "feature/reuse")
        assert task.branch_name == "feature/reuse"

    def test_delegates_validation_to_task(self, service: TaskQueueService) -> None:
        with pytest.raises(ValueError, match="Invalid git branch name"):
            service.add_task("X", "p", "feature/bad name")


class TestListQueue:
    def test_returns_only_queued(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        service.add_task("Queued", "p", "feature/q")
        running_task = Task(
            name="Running",
            prompt="p",
            branch_name="feature/r",
            status=StatusEnum.RUNNING,
            position=1,
        )
        repo.save(running_task)
        queue = service.list_queue()
        assert len(queue) == 1
        assert queue[0].name == "Queued"

    def test_empty_queue(self, service: TaskQueueService) -> None:
        assert service.list_queue() == []


class TestListAllTasks:
    def test_returns_all_statuses(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        service.add_task("Queued", "p", "feature/q")
        done_task = Task(
            name="Done",
            prompt="p",
            branch_name="feature/d",
            status=StatusEnum.DONE,
            position=1,
        )
        repo.save(done_task)
        all_tasks = service.list_all_tasks()
        assert len(all_tasks) == 2
