# domain/ - Innermost Layer

The domain layer contains pure business definitions: data models and port interfaces. It has ZERO external dependencies - no third-party libraries, no framework imports, no references to outer layers.

## What Lives Here

- **models/** - Pure data classes.
  - `Task` (id, prompt, branch, status, created_at)
  - `StatusEnum` (queued, running, paused, done, failed)
  - `RateLimitPattern` (pattern matching data for rate limit detection)
  - `DiffResult` (structured representation of git diff output)
- **ports/** - Abstract Base Classes (ABCs) defining interfaces.
  - `TaskRepository` - persistence operations (CRUD for tasks)
  - `GitPort` - git operations (branch, commit, diff)
  - `SubprocessRunner` - process execution (run claude-code CLI)
  - `RateLimitDetector` - output analysis (detect rate limit patterns)

## Dependencies

- **Depends on:** nothing. This is the innermost layer.
- **Depended on by:** everything. services/ uses ports and models. infra/ implements ports and uses models. ui/ uses models indirectly through services.

## How to Interact

- Import models: `from aihelm.domain.models import Task, StatusEnum`
- Import ports: `from aihelm.domain.ports import TaskRepository, GitPort`
- models/ are imported by every other layer.
- ports/ are implemented by infra/, consumed by services/.

## Rules for AI Agents

1. **NEVER import from infra/, services/, or ui/ here.** The dependency arrow always points inward.
2. **Read `specs/contracts/` before defining or modifying a port.** The contract is the spec; the ABC is the implementation of that spec.
3. **Read `specs/schemas/` before defining or modifying a model.** The schema is the spec; the dataclass conforms to it.
4. **Keep models as plain data.** No side effects, no I/O, no framework dependencies. Use `dataclasses`, `enum`, and standard library types only.
5. **Keep ports abstract.** Define *what*, not *how*. No default implementations in ABCs.
