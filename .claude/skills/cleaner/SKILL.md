---
name: cleaner
description: "Use when the user asks to clean up code, refactor safely, reduce duplication, and improve readability without changing behavior."
---

# Cleaner Skill

## Purpose

The cleaner improves maintainability through safe, behavior-preserving refactoring.

## Responsibilities

- Refactor without changing intended behavior.
- Reduce duplication and simplify complex code paths.
- Improve naming and structure for readability.

## Boundaries

- No feature expansion unless required by refactor.
- Preserve existing external behavior and API contracts.
- Keep refactors incremental and reviewable.
- Do not write or update `README.md`, docs, docstrings, or inline comments.

## Workflow

1. Identify code smells and refactor candidates.
2. Apply small, behavior-preserving changes.
3. Run quick checks/tests if available.
4. Provide before/after summary and any residual risks.

## Refactor Priorities

- Remove dead code.
- Extract repeated logic.
- Clarify function boundaries.
- Improve error handling clarity.
- Tighten types and function contracts.

## SoulSync Notes

- Keep architecture aligned with Core Companion orchestration.
- Keep refactors simple and safe for hackathon iteration speed.
