# Workspace Selection Rules

Business invariants governing workspace selection and persistence.

## Selection Rules

1. **Directory constraint:** A selected workspace path must exist and be a directory.
2. **Activation uniqueness:** At most one workspace may be active at a time.
3. **Last selection wins:** Selecting a workspace marks it active and marks all others inactive.
4. **Idempotent reselection:** Re-selecting an already known path updates its metadata timestamp and keeps a single record.
5. **Non-blocking git warning:** Missing `.git` directory does not block selection; the workspace still becomes active.

## Startup Rules

6. **Startup load:** On app startup, the latest active workspace is loaded from persistence and shown in the UI.
7. **No persisted value:** If no workspace is active, the app starts without an execution workspace selected.
8. **Stale workspace:** A persisted workspace whose path no longer exists or is not a directory is ignored when loading: it is neither returned as active nor listed, and startup proceeds as in rule 7. The record is kept in storage, so it becomes visible again if the directory is restored.

## Execution Rules

9. **Execution cwd source:** Command/process execution must resolve its `cwd` from the active workspace path.
10. **No active workspace:** If there is no active workspace, execution features depending on `cwd` must not proceed silently.

## Persistence Rules

11. **Immediate persistence:** Selecting or changing active workspace is persisted immediately.
12. **Missing storage:** Missing workspace storage is treated as empty state.
