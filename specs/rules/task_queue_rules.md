# Task Queue Rules

Business invariants governing task creation and queue management.

## Creation Rules

1. **Default status:** Every new task starts with status `queued`.
2. **Branch validation:** The `branch_name` field must pass git-check-ref-format validation before the task is created. A branch name must NOT:
   - Contain ASCII control characters (0x00-0x1F, 0x7F)
   - Contain space, `~`, `^`, `:`, `?`, `*`, `[`, or `\`
   - Contain `..` (double dot) anywhere
   - Contain `@{` anywhere
   - Start or end with `.`
   - End with `.lock`
   - Start with `-`
   - End with `/`
   - Contain consecutive slashes `//`
   - Be exactly `@`
3. **Name constraint:** Task name must be between 1 and 200 characters inclusive.
4. **Prompt constraint:** Prompt must be non-empty.
5. **Auto-generated ID:** Task ID is a UUID v4, assigned automatically at creation.
6. **Auto-generated timestamp:** `created_at` is set to current UTC time at creation.
7. **Auto-assigned position:** Position is set to `next_position()` from the repository.

## Queue Rules

8. **Ordering:** Tasks in the queue are displayed and processed in `position` ascending order.
9. **Branch uniqueness:** No two active tasks (status `queued` or `running`) may share the same `branch_name`. A branch name may be reused once the previous task using it has reached a terminal status (`done` or `failed`).

## Persistence Rules

10. **Startup load:** On application startup, the queue is populated from the persisted storage.
11. **Immediate persistence:** Every mutation (create, update, delete) is persisted immediately.
