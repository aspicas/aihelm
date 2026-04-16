# tests/ - All Test Code

Every test for the AIHelm project lives here, organized by type and target layer.

## What Lives Here

### unit/ - Fast, isolated tests
- **unit/domain/** - Pure logic tests for models and port contracts. No mocks needed - domain has no dependencies.
- **unit/services/** - Orchestration tests. Mock all ports, verify service behavior and state transitions.
- **unit/infra/** - Concrete implementation tests. Verify JSON round-trips, git command construction, subprocess output parsing.

### integration/ - End-to-end flows
- Tests that exercise real filesystem and git operations on temporary repositories.
- Slower, uses real implementations wired together.

### bdd/ - Behavior-Driven Development
- **bdd/features/** - Gherkin `.feature` files derived from `specs/rules/`.
- **bdd/steps/** - Thin Python glue that maps Gherkin steps to service and domain calls.

## Dependencies

- Tests import from `src/aihelm/` (domain, services, infra, ui).
- BDD features are derived from `specs/rules/`.
- Tests never import from each other across categories.

## How to Run

```bash
pytest tests/unit/          # all unit tests
pytest tests/unit/domain/   # domain only
pytest tests/unit/services/ # services only
pytest tests/unit/infra/    # infra only
pytest tests/integration/   # integration tests
pytest tests/bdd/           # BDD features
pytest                      # everything
```

## Rules for AI Agents

1. **Write tests BEFORE implementation (TDD).** Red-green-refactor: failing test first, then make it pass, then clean up.
2. **Derive BDD features from `specs/rules/`.** Each business rule should have a corresponding `.feature` file.
3. **unit/services/ tests must mock all ports.** Services should be testable without any real I/O.
4. **unit/infra/ tests use temp directories.** Never touch the real filesystem outside of temp paths.
5. **integration/ tests create throwaway git repos.** Use `tmp_path` fixtures; clean up after.
6. **Keep step definitions thin.** BDD steps should delegate to services/domain, not contain logic themselves.
