# AGENTS.md

## Repo Summary

- `pipeworks_ipc` is a standalone, reusable IPC/hash utility package for the Pipe-Works ecosystem.
- Initial objective is semantic parity with the Axis Descriptor Lab hashing behavior.
- Package must stay minimal, deterministic, and easy to adopt across projects.

## Non-Negotiables

- Determinism first: identical inputs must always produce identical digests.
- Semantic stability: do not change hash behavior silently.
- Zero runtime dependencies for core hashing module (stdlib only).
- Backward compatibility: avoid breaking API changes after first tagged release.
- Clear versioning: behavior-changing updates require explicit release notes.

## Scope Priorities

1. Canonical hashing primitives
- `compute_payload_hash(payload_dict)`
- `compute_system_prompt_hash(prompt_text)`
- `compute_output_hash(output_text)`
- `compute_ipc_id(input_hash, system_prompt_hash, model, temperature, max_tokens, seed)`

2. Optional helper
- A generic provenance hash helper may be added later, but must not replace or alter core IPC semantics.

3. Documentation
- Explain normalization and collision-avoidance choices.
- Provide migration notes for adopters (Axis Descriptor Lab, Name Generator, others).

## Development Workflow

- Python: 3.12+
- Packaging/config: `pyproject.toml`
- Install editable package:
  - `pip install -e .`
- Test:
  - `pytest -v`
- Lint/format/type/security (when configured):
  - `pre-commit run --all-files`

## Testing Expectations

- Unit tests must cover:
  - normalization edge cases
  - hash determinism
  - field-sensitivity (single-field changes alter output)
  - delimiter collision protection in IPC ID construction
- Include parity tests against known fixtures from Axis Descriptor Lab behavior.

## Release Expectations

- Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`).
- Release discipline:
  - Default to `fix:` for repairs, regressions, missing wiring, validation hardening, and docs/code alignment.
  - Use `feat:` only for clearly user-visible net-new capability.
  - If a PR mixes repairs and new capability, split changes (or commits) so release intent is explicit.
- Keep changelog entries explicit about hashing behavior changes.
- Treat behavior changes as high-risk; require test and docs updates together.

## Useful Paths

- Package code: `pipeworks_ipc/`
- Tests: `tests/`
- Working notes: `_working/`
- Package metadata: `pyproject.toml`

## Collaboration Notes

- Prefer small, reviewable PRs per phase.
- If semantics are unclear, preserve Axis Descriptor Lab behavior by default and document assumptions.
