from aihelm.domain.models.status import StatusEnum


class TestStatusEnum:
    def test_has_five_members(self) -> None:
        assert len(StatusEnum) == 5

    def test_queued_value(self) -> None:
        assert StatusEnum.QUEUED == "queued"

    def test_running_value(self) -> None:
        assert StatusEnum.RUNNING == "running"

    def test_paused_value(self) -> None:
        assert StatusEnum.PAUSED == "paused"

    def test_done_value(self) -> None:
        assert StatusEnum.DONE == "done"

    def test_failed_value(self) -> None:
        assert StatusEnum.FAILED == "failed"

    def test_is_str_subclass(self) -> None:
        assert isinstance(StatusEnum.QUEUED, str)
