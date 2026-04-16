# ui/ - Presentation Layer (Flet Desktop UI)

The UI layer renders the desktop interface using Flet. It translates user actions into service calls and displays results.

## What Lives Here

- **components/** - Reusable Flet controls (building blocks).
  - Status badge (colored indicator for task status)
  - Task card (summary view of a single task)
  - Console panel (live output stream from workers)
  - Emergency stop button (kill all running workers)
- **views/** - Page compositions that assemble components into screens.
  - Queue view (main task list with controls)
  - Diff review modal (review generated changes before committing)

## Dependencies

- **Depends on:** `services/` (public interfaces only).
- **Depended on by:** nothing. This is the outermost layer facing the user.

## How to Interact

- Views hold references to services and call their methods:
  ```python
  self.queue_service.add_task(prompt, branch)
  ```
- Components receive data (domain models) and callbacks (service methods) as constructor parameters.
- Components are reusable across views. Views are one-per-screen.

## Rules for AI Agents

1. **NEVER import from domain/ports or infra/.** The UI interacts with the system only through services.
2. **Importing domain/models is OK** for type hints and reading data (e.g., `Task`, `StatusEnum`).
3. **Components are reusable.** They should not contain business logic or direct service calls. Pass callbacks in.
4. **Views compose components.** A view wires components together and connects them to services.
5. **Keep UI logic minimal.** Display formatting and user input handling belong here. Business decisions belong in services.
