---
id: SPEC-001
title: Basic pomodoro timer
status: Done
priority: High
labels: [logic, ui]
created: 2026-09-30
completed: 2026-09-30
adr: [ADR-0001, ADR-0002, ADR-0004]
---

# SPEC-001: Basic pomodoro timer

## Problem
I want a small standalone Windows desktop app for the [Pomodoro Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique): focused work intervals with short breaks, and a long break after a few rounds.

## Scope
- Three modes with defaults: Pomodoro 25 min, Short break 5 min, Long break 15 min.
- Set durations, Start, Pause/Resume, Reset, Skip.
- Automatic cycle: short break after each pomodoro, long break after every N (default 4).
- Alert when a period ends: sound, window brought to front; next period waits for the user.
- Settings remembered between runs.
- Keyboard: `Space` start/pause, `R` reset.

### Out of scope
- Statistics across days, task lists, tray icon.

## Acceptance criteria
- [x] Runs on Windows with `py pomodoro.py` or by double-clicking `pomodoro.pyw`
- [x] Countdown stays accurate while paused/resumed
- [x] Cycle order is P S P S P S P L
- [x] A skipped pomodoro isn't counted
- [x] Custom durations survive a restart; corrupt settings file falls back to defaults
- [x] Can be built to a standalone `.exe` with PyInstaller (`build.ps1`)
