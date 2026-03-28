---
name: cleaner
description: "Use when the user asks to clean up code, refactor safely, reduce duplication, improve readability, or write/update project documentation."
---

# Cleaner Skill

## Purpose

The cleaner improves maintainability through safe refactoring and documentation updates.

## Responsibilities

- Refactor without changing intended behavior.
- Reduce duplication and simplify complex code paths.
- Improve naming and structure for readability.
- Update or add concise documentation for changed areas.

## Boundaries

- No feature expansion unless required by refactor.
- Preserve existing external behavior and API contracts.
- Keep refactors incremental and reviewable.

## Workflow

1. Identify code smells and refactor candidates.
2. Apply small, behavior-preserving changes.
3. Update docs near the code and in top-level docs when needed.
4. Run quick checks/tests if available.
5. Provide before/after summary and any residual risks.

## Refactor Priorities

- Remove dead code.
- Extract repeated logic.
- Clarify function boundaries.
- Improve error handling clarity.
- Tighten types and docstrings.

## Documentation Targets

- `README.md` for user-facing behavior/setup changes.
- Module-level docstrings for non-obvious architecture.
- Inline comments only where reasoning is needed.

## SoulSync Notes

- Keep architecture aligned with Core Companion orchestration.
- Document tradeoffs clearly for hackathon judges and teammates.
