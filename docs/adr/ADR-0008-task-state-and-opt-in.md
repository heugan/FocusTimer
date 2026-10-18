---
id: ADR-0008
title: Opt-in task feature with separate task state and pure logic classes
status: Accepted
date: 2026-10-02
specs: [SPEC-009, SPEC-010, SPEC-011]
---

# ADR-0008: Opt-in task feature with separate task state and pure logic classes

## Context
The task and work-log feature (SPEC-009 and SPEC-010) adds UI, files and state to a timer that many users want to keep simple. Parked tasks must survive restarts. The feature also has to be implementable and testable by a developer who is new to the codebase.

## Decision
1. **Feature flag**: `Settings.work_log: bool = False`. When it is off, no task UI is built or shown, and no task or log files are read or written. The app is the plain timer.
2. **Separate state file**: the current task, the current note and the parked stack are stored in `%APPDATA%\Pomodoro\tasks.json`, which has its own `version` field. They are kept out of `settings.json` because they are working data that changes all the time, not preferences. They are kept out of the log because the log is a history that is only ever added to.
3. **Pure, testable logic** following ADR-0002, with no Tk in these units:
   - `clean_text()`: sanitises free text (SPEC-011).
   - `WorkLog`: formats lines and appends them to the correct monthly file. It takes an injectable clock and folder.
   - `TaskBoard`: holds the current task and note and the parked stack. It handles park, resume, remove and complete, and loads and saves itself.

   `PomodoroApp` only wires UI events to these units and renders their state.

## Alternatives considered
- **Feature always on**: makes the default experience heavier for users who only want a timer.
- **Task state inside `settings.json`**: mixes preferences with working data, and every keystroke would rewrite the settings.
- **Rebuilding the state from the log**: fragile, and it would make the log the source of truth for the UI.

## Consequences
- The feature can be delivered and reviewed in steps: SPEC-011, then SPEC-009, then SPEC-010.
- Turning the feature off keeps existing data on disk, so turning it back on restores everything.
- There are three small classes to keep consistent: text is always cleaned before it reaches `TaskBoard` or `WorkLog`.
