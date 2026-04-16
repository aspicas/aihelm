# AIHelm - Local Orchestrator for AI Code Assistants

## What is this project

Desktop application (Python/Flet) that queues, executes, and supervises tasks delegated to AI CLIs (claude-code). Automatically manages Git branches, detects rate limits, and provides visual diff review before committing.

**Stack**: Python 3.11+, Flet (UI), subprocess (CLI execution), threading (worker daemon)
**Platforms**: macOS, Windows, Linux

---

## Architecture

Clean Architecture with 4 layers. Dependencies flow inward:

```
UI -> Services -> Domain (ports) <- Infra
```

- **Domain** (`src/aihelm/domain/`): Pure models and ABCs (ports). No external dependencies.
- **Services** (`src/aihelm/services/`): Orchestration logic. Depends only on domain.
- **Infra** (`src/aihelm/infra/`): Concrete implementations (JSON, Git, subprocess).
- **UI** (`src/aihelm/ui/`): Flet components and views.

---

## Folder Structure

```
specs/                          # Source of truth (SDD)
  contracts/                    # Interface/port definitions in Markdown/YAML
  schemas/                      # Data JSON schemas
  rules/                        # Business invariants, state rules

src/aihelm/                     # Python package (src layout)
  domain/
    models/                     # Task, StatusEnum, RateLimitPattern, DiffResult
    ports/                      # ABCs: TaskRepository, GitPort, SubprocessRunner, RateLimitDetector
  services/                     # TaskQueueService, WorkerService, RateLimitService
  infra/
    persistence/                # JsonTaskRepository (tasks.json)
    subprocess/                 # Popen wrapper for claude-code
    git/                        # Git operations via shell
  ui/
    components/                 # Reusable Flet controls
    views/                      # Page compositions

tests/
  unit/domain/                  # Pure logic tests, no mocks
  unit/services/                # Tests with mocked/faked ports
  unit/infra/                   # Concrete infra tests
  integration/                  # E2E flows with real filesystem and git
  bdd/features/                 # Gherkin .feature files
  bdd/steps/                    # Step implementations (pytest-bdd)
```

---

## Design Decisions

| Decision | Reason |
|----------|--------|
| src/ layout | Avoids import shadowing during development (PEP 517) |
| Ports as ABCs | Dependency Inversion: domain defines contracts, infra implements them |
| specs/ separate from code | SDD: specs are the source of truth, reviewed independently |
| JSON for v1 persistence | YAGNI: SQLite is unnecessary for a local task queue |
| No config/ directory | KISS: minimal configuration in v1, a single module suffices |
| No event bus/mediator | KISS: 3 layers + UI is enough for a v1 desktop app |
| Worker as daemon thread | SRS requirement: must not block the Flet event loop |

---

## SDD (Spec Driven Development)

Specs in `specs/` are the source of truth. The workflow is:

1. Write contract in `specs/contracts/` (e.g., `task_repository.md`)
2. Define schema in `specs/schemas/` (e.g., `task.json`)
3. Document rules in `specs/rules/` (e.g., `task_state_transitions.md`)
4. Implement port in `domain/ports/` reflecting the contract
5. Implement in `infra/` or `services/` as appropriate

**Rule**: If code contradicts the spec, the spec wins. Update the code, not the spec (unless explicitly decided otherwise).

---

## BDD/TDD

### BDD Workflow
1. Read rule in `specs/rules/`
2. Write Gherkin scenario in `tests/bdd/features/`
3. Implement steps in `tests/bdd/steps/`
4. Write code until it passes

### TDD Workflow
1. Write unit test in `tests/unit/`
2. Implement the minimum code to make it pass
3. Refactor while keeping tests green

### Running tests
```bash
pytest tests/unit/               # Unit tests
pytest tests/integration/        # Integration tests
pytest tests/bdd/                # BDD tests
pytest                           # All
```

---

## Multi-Agent Collaboration

### Work Rules

1. **Read CLAUDE.md first**: Any new agent starts here
2. **Read specs before implementing**: `specs/contracts/` defines what to build
3. **One agent per layer**: Avoid two agents modifying the same layer simultaneously
4. **Ports are the contract**: If you need something from another layer, define/use a port in `domain/ports/`
5. **Tests accompany code**: Never open a PR without corresponding tests

### Safe Parallel Work Zones

| Agent | Zone | Reads from |
|-------|------|------------|
| A | `infra/git/` | `specs/contracts/git_manager.md`, `domain/ports/` |
| B | `services/` | `specs/rules/`, `domain/ports/` |
| C | `ui/views/` | `services/` (public interfaces) |
| D | `tests/bdd/` | `specs/rules/`, `specs/schemas/` |

### Avoiding Context Loss

- Specs document the "what" and "why"
- Ports document the "how it connects"
- Tests document the "how to verify"
- This file documents the "how to work"

An agent can reconstruct the full system state by reading: `CLAUDE.md` -> `specs/` -> `domain/ports/` -> relevant tests.

---

## Conventions

- **Naming**: snake_case for modules and functions. PascalCase for classes.
- **Imports**: Never import from infra/ui in domain/services. Only through ports.
- **Commits**: Conventional commits enforced by pre-commit hook. Prefixes: `feat:`, `fix:`, `refactor:`, `test:`, `spec:`, `docs:`, `ci:`, `chore:`, `build:`
- **Branches**: `feature/<name>`, `fix/<name>`, `refactor/<name>`

---

## CI & Quality Gates

### Pre-Commit Hooks (`.pre-commit-config.yaml`)
Run automatically on every commit:
- Ruff (lint + format)
- Mypy (type check)
- Bandit (security scan)
- Conventional commit message validation
- No direct commits to `main`
- Secret/large file detection

Install: `pre-commit install --install-hooks`
Run manually: `pre-commit run --all-files`

### GitHub Actions (`.github/workflows/`)
- **ci.yml**: Runs on push to `main` and on PRs. Jobs: lint, typecheck, test (matrix: 3 OS x 3 Python versions), coverage.
- **pr-checks.yml**: Validates PR title convention and warns if ports/models changed without updating specs.

---

## Updating CLAUDE.md

This file should be updated when:
- A new significant layer or module is added
- A new architectural decision is made
- Work conventions change
- A recurring pattern is identified that other agents should know about

**Who updates**: The agent introducing the change. Do not delegate.
**Format**: Keep existing sections. Append to the relevant section.
