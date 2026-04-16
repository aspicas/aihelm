# Contributing to AIHelm

Thanks for your interest in contributing to AIHelm! This project is free software licensed under GPL-3.0, and community contributions are welcome.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/<your-username>/aihelm.git
cd aihelm
```

### 2. Set Up Your Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Install Pre-Commit Hooks

```bash
pre-commit install --install-hooks
```

This installs hooks that run automatically on every commit:
- **Trailing whitespace / EOF fixer** — clean formatting
- **Ruff** — linting + auto-format (replaces Black, isort, flake8)
- **Mypy** — static type checking
- **Bandit** — security analysis
- **Conventional commit** — enforces commit message format (`feat:`, `fix:`, etc.)
- **No commit to main** — blocks direct pushes to `main`
- **Large file check** — prevents files >500KB from being committed
- **Secret detection** — blocks private keys from being committed

### 4. Verify Everything Works

```bash
pytest
pre-commit run --all-files
```

## How to Contribute

### Reporting Bugs

Open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- OS and Python version
- Relevant logs or error output

### Suggesting Features

Open an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Whether it fits v1 scope (see README.md)

### Submitting Code

1. **Check existing issues** — avoid duplicate work.
2. **Open an issue first** for non-trivial changes. Discuss the approach before writing code.
3. **Fork the repo and create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Follow the development workflow** (see below).
5. **Submit a Pull Request** against `main`.

## Development Workflow

AIHelm follows **Spec Driven Development (SDD)**, **Test Driven Development (TDD)**, and **Behavior Driven Development (BDD)**. This means:

### For New Features

1. Write or update the spec in `specs/` (contract, schema, or rule)
2. Write a failing test (`tests/unit/` or `tests/bdd/features/`)
3. Implement the minimum code to pass
4. Refactor while keeping tests green
5. Commit

### For Bug Fixes

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify the test passes
4. Check if `specs/` needs updating
5. Commit

## Architecture Rules

The project uses Clean Architecture. **These rules are strictly enforced:**

```
UI  ->  Services  ->  Domain (ports)  <-  Infra
```

- **domain/** never imports from services/, infra/, or ui/
- **services/** imports only from domain/ (models and ports)
- **infra/** implements domain/ports — never imported directly by services/ or ui/
- **ui/** interacts with the system only through services/

If your PR violates layer boundaries, it will be requested to change.

Each layer has a `README.md` explaining its dependencies and interaction rules. Read the one for the layer you're modifying.

## Code Style

### Naming

- `snake_case` for modules, functions, and variables
- `PascalCase` for classes
- Descriptive names over abbreviations

### Formatting

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Max line length: 88 characters (Black default)
- Use type hints for public function signatures

### Imports

- Standard library first, then third-party, then project imports
- Never import from a layer that your layer shouldn't depend on

## Commit Messages

Use prefixes to categorize changes:

| Prefix | Use for |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `refactor:` | Code restructuring (no behavior change) |
| `test:` | Adding or updating tests |
| `spec:` | Adding or updating specs |
| `docs:` | Documentation changes |

Examples:
```
feat: add rate limit pattern configuration
fix: worker thread not terminating on app close
test: add unit tests for task state transitions
spec: define git port contract
```

Keep commits atomic — one logical change per commit.

## Branch Naming

```
feature/<short-description>
fix/<short-description>
refactor/<short-description>
```

## Pull Request Guidelines

- **One concern per PR.** Don't mix a feature with an unrelated refactor.
- **Include tests.** PRs without tests for new or changed behavior will be requested to add them.
- **Update specs if needed.** If your change modifies a contract, schema, or business rule, update `specs/` in the same PR. CI will warn you if ports/models changed without corresponding spec updates.
- **Keep PRs reviewable.** Prefer smaller, focused PRs over large ones. If a change is big, break it into a series.
- **Fill in the PR template.** The repo includes a PR template with checklists — complete all relevant items.
- **PR title must follow conventional commits.** Same format as commit messages (e.g., `feat: add queue reordering`). CI enforces this.

## Testing

All tests live in `tests/` and run with pytest:

```bash
pytest tests/unit/           # Fast, isolated unit tests
pytest tests/unit/domain/    # Domain logic only
pytest tests/unit/services/  # Service orchestration only
pytest tests/unit/infra/     # Infrastructure only
pytest tests/integration/    # End-to-end (slower, uses real git)
pytest tests/bdd/            # BDD scenarios
pytest                       # Everything
```

**Requirements:**
- Unit tests must not perform I/O. Mock all ports in service tests.
- Integration tests must use temporary directories. Never touch the real filesystem outside `tmp_path`.
- BDD features must trace back to a rule in `specs/rules/`.

## What's Out of Scope for v1

Before investing time on a contribution, check that it fits the current scope:

- No cloud sync or user accounts
- No automatic PR creation
- No multiple simultaneous AI assistants
- No plugin system

These are planned for future versions. If you want to work on them, open an issue to discuss timing and approach first.

## Code of Conduct

Be respectful, constructive, and inclusive. We're all here to build something useful together.

- Be kind in code reviews
- Assume good intentions
- Focus on the code, not the person
- Welcome newcomers

## Questions?

Open an issue with the `question` label. We're happy to help you get oriented.
