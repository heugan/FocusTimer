---
id: SPEC-006
title: Show progress through the pomodoro session
status: Done
priority: Medium
labels: [ui]
created: 2026-10-01
completed: 2026-10-01
adr: [ADR-0005]
---

# SPEC-006: Show progress through the pomodoro session

## Problem
It's hard to tell where you are in a cycle: which pomodoro this is, what comes next, and how far into the current period you are.

## Scope
A **Session** card where the settings panel used to be:
- Step track for one cycle (P S P S P S P L): large dots = pomodoros, small = short breaks, medium = long break, each in its mode's accent colour. Done steps filled, current step a ring, upcoming grey.
- "Pomodoro 2 of 4" (or the break name) and "Next: …".
- Progress bar of the current period with "9 of 25 min · 37%".
- "Pomodoros completed: N" for this run of the app.

## Acceptance criteria
- [x] Track length follows the "Long break after" setting
- [x] Current step correct through a full cycle, including the finished state
- [x] Progress bar fills from 0 to 100 % over the period

### Out of scope
- History across app restarts / days.
