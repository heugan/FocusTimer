---
id: ADR-0002
title: Timer logic separate from UI, driven by a monotonic clock
status: Accepted
date: 2026-09-30
specs: [SPEC-001, SPEC-005, SPEC-006]
---

# ADR-0002: Timer logic separate from UI, driven by a monotonic clock

## Context
Timer behaviour (pause/resume, cycle order, finished state, progress) is the part most likely to have bugs and should be testable without opening a window. Tk's `after()` callbacks are not precise and drift if counted.

## Decision
We will keep all timer and cycle rules in `PomodoroSession`, a plain class with no Tk imports used at runtime. It stores an end timestamp from an injectable clock (`time.monotonic` by default) instead of counting ticks. The UI polls `tick()` every 200 ms and only renders state.

## Alternatives considered
- **Decrement a counter on each `after(1000)`** — drifts and breaks when the window is busy.
- **Logic inside the Tk class** — untestable without a display.

## Consequences
- Unit tests use a fake clock (`test_pomodoro.py`) and run in milliseconds.
- New behaviour (e.g. the finished/Next state in SPEC-005, `cycle_steps()` in SPEC-006) is added to the session first, with tests, then rendered.
