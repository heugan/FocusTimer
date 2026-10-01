---
id: ADR-0004
title: Store settings as JSON in %APPDATA%\Pomodoro
status: Accepted
date: 2026-09-30
specs: [SPEC-001]
---

# ADR-0004: Store settings as JSON in %APPDATA%\Pomodoro

## Context
Settings must survive restarts, including when the app runs as a PyInstaller `.exe` from a read-only or temporary location.

## Decision
We will store the `Settings` dataclass as JSON in `%APPDATA%\Pomodoro\settings.json`. Loading validates each field against its default's type (ints ≥ 1, sound name in the known list) and falls back to the default per field; a missing or corrupt file yields all defaults. New fields therefore need no migration.

## Alternatives considered
- **Next to the executable** — breaks for installed/onefile builds.
- **Windows registry** — harder to inspect and reset.

## Consequences
- Users can reset by deleting the file.
- Adding a setting = adding a dataclass field with a default.
