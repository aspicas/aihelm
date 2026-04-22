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


class TestUpdateTask:
    def test_updates_name(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = service.add_task("Old", "p", "feature/x")
        updated = service.update_task(
            task.id, name="New", prompt="p", branch_name="feature/x"
        )
        assert updated.name == "New"
        assert updated.id == task.id
        assert updated.created_at == task.created_at
        assert updated.position == task.position

    def test_updates_prompt(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = service.add_task("T", "old prompt", "feature/x")
        updated = service.update_task(
            task.id, name="T", prompt="new prompt", branch_name="feature/x"
        )
        assert updated.prompt == "new prompt"

    def test_updates_branch_name(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = service.add_task("T", "p", "feature/old")
        updated = service.update_task(
            task.id, name="T", prompt="p", branch_name="feature/new"
        )
        assert updated.branch_name == "feature/new"

    def test_updates_multiple_fields(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = service.add_task("A", "pa", "feature/a")
        updated = service.update_task(
            task.id, name="B", prompt="pb", branch_name="feature/b"
        )
        assert updated.name == "B"
        assert updated.prompt == "pb"
        assert updated.branch_name == "feature/b"

    def test_rejects_nonexistent_task(self, service: TaskQueueService) -> None:
        with pytest.raises(ValueError, match="Task not found"):
            service.update_task(
                "nonexistent-id", name="X", prompt="p", branch_name="feature/x"
            )

    def test_rejects_edit_of_running_task(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = Task(
            name="R",
            prompt="p",
            branch_name="feature/r",
            status=StatusEnum.RUNNING,
            position=0,
        )
        repo.save(task)
        with pytest.raises(ValueError, match="Only queued tasks can be edited"):
            service.update_task(
                task.id, name="New", prompt="p", branch_name="feature/r"
            )

    def test_rejects_edit_of_done_task(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = Task(
            name="D",
            prompt="p",
            branch_name="feature/d",
            status=StatusEnum.DONE,
            position=0,
        )
        repo.save(task)
        with pytest.raises(ValueError, match="Only queued tasks can be edited"):
            service.update_task(
                task.id, name="New", prompt="p", branch_name="feature/d"
            )

    def test_rejects_edit_of_failed_task(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = Task(
            name="F",
            prompt="p",
            branch_name="feature/f",
            status=StatusEnum.FAILED,
            position=0,
        )
        repo.save(task)
        with pytest.raises(ValueError, match="Only queued tasks can be edited"):
            service.update_task(
                task.id, name="New", prompt="p", branch_name="feature/f"
            )

    def test_rejects_edit_of_paused_task(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = Task(
            name="P",
            prompt="p",
            branch_name="feature/p",
            status=StatusEnum.PAUSED,
            position=0,
        )
        repo.save(task)
        with pytest.raises(ValueError, match="Only queued tasks can be edited"):
            service.update_task(
                task.id, name="New", prompt="p", branch_name="feature/p"
            )

    def test_rejects_duplicate_branch_on_edit(self, service: TaskQueueService) -> None:
        service.add_task("A", "p", "feature/a")
        task_b = service.add_task("B", "p", "feature/b")
        with pytest.raises(ValueError, match="already assigned"):
            service.update_task(
                task_b.id, name="B", prompt="p", branch_name="feature/a"
            )

    def test_allows_keeping_same_branch(self, service: TaskQueueService) -> None:
        task = service.add_task("T", "p", "feature/keep")
        updated = service.update_task(
            task.id, name="New Name", prompt="p", branch_name="feature/keep"
        )
        assert updated.branch_name == "feature/keep"
        assert updated.name == "New Name"

    def test_allows_branch_reuse_from_done_task(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        done_task = Task(
            name="Done",
            prompt="p",
            branch_name="feature/reuse",
            status=StatusEnum.DONE,
            position=0,
        )
        repo.save(done_task)
        task = service.add_task("Active", "p", "feature/active")
        updated = service.update_task(
            task.id, name="Active", prompt="p", branch_name="feature/reuse"
        )
        assert updated.branch_name == "feature/reuse"

    def test_validates_name_on_edit(self, service: TaskQueueService) -> None:
        task = service.add_task("T", "p", "feature/x")
        with pytest.raises(ValueError, match="name"):
            service.update_task(task.id, name="", prompt="p", branch_name="feature/x")

    def test_validates_branch_on_edit(self, service: TaskQueueService) -> None:
        task = service.add_task("T", "p", "feature/x")
        with pytest.raises(ValueError, match="Invalid git branch name"):
            service.update_task(
                task.id, name="T", prompt="p", branch_name="feature/bad name"
            )

    def test_persists_changes(
        self, repo: InMemoryTaskRepository, service: TaskQueueService
    ) -> None:
        task = service.add_task("Old", "p", "feature/x")
        service.update_task(task.id, name="New", prompt="p", branch_name="feature/x")
        stored = repo.get(task.id)
        assert stored is not None
        assert stored.name == "New"


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
