# WorkspaceRepository Contract

Port interface for persisting and retrieving project workspaces used as execution roots.

## Operations

### list_all() -> list[Workspace]

Return all known workspaces ordered by `selected_at` descending (most recently selected first).

### get_active() -> Workspace | None

Return the currently active workspace. Returns `None` when no workspace is active.

### upsert(workspace: Workspace) -> Workspace

Persist a workspace. If a workspace with the same normalized path already exists, it is updated
in place and keeps its identity.

**Postcondition:** `list_all()` contains exactly one entry for that path.

### set_active(workspace_id: str) -> Workspace

Mark the workspace identified by `workspace_id` as active and mark every other workspace inactive.

**Postcondition:** `get_active()` returns the same workspace.

### remove(workspace_id: str) -> None

Remove the workspace identified by `workspace_id`. No-op if it does not exist.

## Constraints

- **Atomic writes:** Failed writes must not corrupt existing data.
- **Thread safety:** Concurrent reads must not raise. Writes are serialized.
- **Configurable path:** Storage file location is provided at construction time.
- **Missing storage:** If storage does not exist, reads return empty results (do not raise).
- **Single active workspace:** At most one workspace can be active at any time.
