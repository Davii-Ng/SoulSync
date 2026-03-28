---
name: coder
description: "Use when the user asks to implement features, fix bugs, or write code. Produces code changes and concise explanatory comments for non-obvious snippets."
---

# Coder Skill

## Purpose

The coder implements planned changes in project code and explains non-obvious logic with concise comments.

## Responsibilities

- Implement only what is in scope.
- Preserve existing style and conventions.
- Add short, useful comments for complex logic blocks.
- Keep public APIs stable unless change is required.
- Validate changes with quick checks when possible.

## Coding Rules

- Prefer minimal, focused diffs.
- Avoid unrelated formatting-only edits.
- Use meaningful names and type hints where appropriate.
- Add comments only where code intent is not obvious.
- Never commit secrets or hardcoded API keys.

## Workflow

1. Read relevant files and understand current behavior.
2. Implement code with smallest safe change.
3. Add concise comments to explain complex sections.
4. Run lightweight validation (lint/test/compile when feasible).
5. Summarize changed files and behavior.

## Comment Style Guide

- Good comment: explains why a block exists or a tricky assumption.
- Avoid comment noise that repeats the code.
- Keep comments short and technical.

## SoulSync Notes

- Frontend: React + TypeScript strict, functional components.
- Backend: FastAPI with snake_case and type hints where possible.
- Multi-agent orchestration flows through Core Companion.
