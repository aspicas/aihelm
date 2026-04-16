# specs/ - SDD Source of Truth

The Software Design Documents in this directory are the authoritative specification for the AIHelm project. All implementation code must conform to what is defined here.

## What Lives Here

- **contracts/** - Interface definitions. Describes what each domain port must provide (method signatures, return types, error conditions).
- **schemas/** - Data shapes. Defines the structure of every model: fields, types, constraints, defaults.
- **rules/** - Business invariants. Conditions that must always hold true (e.g., task state transitions, rate limit thresholds, queue ordering).

## Dependencies

- **Depends on:** nothing. Specs are pure documentation.
- **Depended on by:** domain/ports (implements contracts), domain/models (conforms to schemas), services (follows rules), tests/bdd (derives features from rules).

## How to Interact

- Specs are consumed by reading them. They never import code and code never imports them at runtime.
- `contracts/` maps 1:1 to ABCs in `domain/ports/`.
- `schemas/` maps 1:1 to dataclasses in `domain/models/`.
- `rules/` maps 1:1 to Gherkin features in `tests/bdd/features/`.

## Rules for AI Agents

1. **Read specs BEFORE writing any implementation code.** Always check the relevant contract, schema, or rule first.
2. **If code contradicts a spec, the spec wins.** Fix the code, not the spec (unless the spec itself needs a deliberate update).
3. **Update specs when requirements change.** A spec change is a deliberate act - commit it separately from code changes when possible.
4. **Keep specs language-agnostic.** They describe *what*, not *how*. No Python syntax, no framework details.
