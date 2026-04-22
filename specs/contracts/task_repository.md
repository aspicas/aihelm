# TaskRepository Contract

Port interface for persisting and retrieving tasks.

## Operations

### save(task: Task) -> None

Persist a task. If a task with the same `id` already exists, it is replaced (upsert).

**Postcondition:** `get(task.id)` returns a task equal to the one saved.

### get(task_id: str) -> Task | None

Retrieve a task by its unique ID. Returns `None` if no task with that ID exists.

### list_by_status(status: StatusEnum) -> list[Task]

Return all tasks matching the given status, ordered by `position` ascending.

### list_all() -> list[Task]

Return all tasks regardless of status, ordered by `position` ascending.

### delete(task_id: str) -> None

Remove the task with the given ID. No-op if the task does not exist.

### next_position() -> int

Return the next available position number: `max(position) + 1` across all tasks, or `0` if the repository is empty.

## Constraints

- **Atomic writes:** A failed write must not corrupt existing data.
- **Thread safety:** Concurrent reads must not raise errors. Writes are serialized.
- **Configurable path:** The storage location (file path) is provided at construction time.
- **Missing storage:** If the backing store does not exist on read, return empty results (do not raise).
