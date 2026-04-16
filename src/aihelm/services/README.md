# services/ - Application Orchestration Layer

The services layer coordinates business operations by combining domain models and ports. It contains the application's "use cases" - the things the system actually does.

## What Lives Here

- **TaskQueueService** - Manages the task queue: add, reorder, prioritize, dequeue tasks.
- **WorkerService** - Controls worker lifecycle: start/stop daemon threads, assign tasks, handle completion/failure.
- **RateLimitService** - Monitors subprocess output for rate limit patterns, triggers pause/resume logic.

## Dependencies

- **Depends on:** `domain/models` and `domain/ports` ONLY.
- **Depended on by:** `ui/views` (views call service methods to drive the application).

## How to Interact

- Services receive port implementations via constructor injection:
  ```python
  service = TaskQueueService(repo=json_task_repo)
  ```
- UI views hold references to services and call their public methods.
- Services call port methods (e.g., `self.repo.save(task)`) - they never know the concrete implementation.

## Rules for AI Agents

1. **NEVER import from infra/ directly.** Use dependency injection. If you need a concrete class, you're in the wrong layer.
2. **Depend only on domain/.** All imports should be `from aihelm.domain.models import ...` or `from aihelm.domain.ports import ...`.
3. **Read `specs/rules/` for business logic.** The rules define invariants your service must enforce (e.g., valid state transitions, queue constraints).
4. **Test with mocked ports.** Unit tests live in `tests/unit/services/` and inject mock implementations of ports.
5. **Keep services stateless where possible.** State belongs in models persisted through ports, not in service instance variables.
