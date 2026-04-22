import uuid
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from aihelm.domain.models.status import StatusEnum
from aihelm.domain.models.task import Task


class TestTaskCreation:
    def test_defaults(self) -> None:
        task = Task(name="Fix bug", prompt="Fix it", branch_name="feature/fix")
        assert task.status == StatusEnum.QUEUED
        assert task.position == 0
        assert isinstance(task.created_at, datetime)
        uuid.UUID(task.id)  # validates it's a valid UUID

    def test_explicit_fields(self) -> None:
        dt = datetime(2026, 1, 1, tzinfo=UTC)
        task = Task(
            name="Test",
            prompt="Do it",
            branch_name="fix/test",
            id="abc-123",
            status=StatusEnum.RUNNING,
            created_at=dt,
            position=5,
        )
        assert task.id == "abc-123"
        assert task.status == StatusEnum.RUNNING
        assert task.created_at == dt
        assert task.position == 5

    def test_frozen(self) -> None:
        task = Task(name="X", prompt="Y", branch_name="feature/x")
        with pytest.raises(FrozenInstanceError):
            task.name = "Z"  # type: ignore[misc]


class TestTaskNameValidation:
    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Task(name="", prompt="p", branch_name="feature/ok")

    def test_max_length_accepted(self) -> None:
        task = Task(name="a" * 200, prompt="p", branch_name="feature/ok")
        assert len(task.name) == 200

    def test_over_max_length_rejected(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Task(name="a" * 201, prompt="p", branch_name="feature/ok")


class TestPromptValidation:
    def test_empty_prompt_rejected(self) -> None:
        with pytest.raises(ValueError, match="Prompt"):
            Task(name="X", prompt="", branch_name="feature/ok")


class TestBranchNameValidation:
    @pytest.mark.parametrize(
        "branch",
        [
            "feature/ok",
            "fix/bug-123",
            "feature/a/b/c",
            "my-branch",
            "release/v1.0.0",
            "feat/CAPS-ok",
        ],
    )
    def test_valid_names(self, branch: str) -> None:
        task = Task(name="T", prompt="P", branch_name=branch)
        assert task.branch_name == branch

    @pytest.mark.parametrize(
        ("branch", "reason"),
        [
            ("feature/bad name", "space"),
            ("feature/a..b", "double dot"),
            ("feature/@{ref}", "at-brace"),
            (".hidden", "leading dot"),
            ("feature/end.", "trailing dot"),
            ("feature/main.lock", ".lock suffix"),
            ("feature/a~1", "tilde"),
            ("feature\\name", "backslash"),
            ("feature/a^b", "caret"),
            ("feature/a:b", "colon"),
            ("feature/a?b", "question mark"),
            ("feature/a*b", "asterisk"),
            ("feature/a[b", "bracket"),
            ("-leading-dash", "leading dash"),
            ("feature/trailing/", "trailing slash"),
            ("feature//double", "consecutive slashes"),
            ("@", "bare at"),
        ],
    )
    def test_invalid_names(self, branch: str, reason: str) -> None:
        with pytest.raises(ValueError, match="Invalid git branch name"):
            Task(name="T", prompt="P", branch_name=branch)
