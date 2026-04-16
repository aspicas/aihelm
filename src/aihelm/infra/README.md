# infra/ - Outer Layer (Concrete Implementations)

The infrastructure layer provides concrete implementations of domain ports. This is where I/O happens: disk access, subprocess calls, git commands.

## What Lives Here

- **persistence/** - `JsonTaskRepository` implements `TaskRepository`. Reads/writes tasks as JSON files.
- **subprocess/** - Popen wrapper implements `SubprocessRunner`. Launches and manages claude-code CLI processes.
- **git/** - Shell-based git operations implement `GitPort`. Runs git commands via subprocess.

## Dependencies

- **Depends on:** `domain/ports` (implements them), `domain/models` (uses them).
- **Depended on by:** the app's dependency injection wiring at startup. Nothing else imports infra/ directly.

## How to Interact

- Each subdirectory implements exactly one port from `domain/ports/`.
- Implementations are wired to services at app startup via constructor injection:
  ```python
  repo = JsonTaskRepository(path="~/.aihelm/tasks.json")
  service = TaskQueueService(repo=repo)
  ```
- Services and UI never import from infra/. They depend on the port abstraction.

## Rules for AI Agents

1. **One subdirectory per port.** `persistence/` implements `TaskRepository`, `subprocess/` implements `SubprocessRunner`, `git/` implements `GitPort`.
2. **Read the corresponding `specs/contracts/` before implementing.** The contract defines what the port requires; your implementation must satisfy every clause.
3. **Test in `tests/unit/infra/`.** Test JSON round-trips, git command construction, output parsing. Use temp directories for filesystem tests.
4. **NEVER be imported by services/ or ui/.** If a service needs your code, it should depend on the port interface instead.
5. **Handle I/O errors gracefully.** Translate low-level exceptions into domain-meaningful errors that services can reason about.
