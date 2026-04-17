from enum import StrEnum


class StatusEnum(StrEnum):
    """Lifecycle states of a task."""

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    FAILED = "failed"
