---
id: SPEC-005
title: Skip becomes Next when a period ends
status: Done
priority: Medium
labels: [logic, ui]
created: 2026-10-01
completed: 2026-10-01
adr: [ADR-0002]
---

# SPEC-005: Skip becomes Next when a period ends

## Problem
When a period ended the app silently jumped to the next mode, so you couldn't see that the timer had finished, and "Skip" was the wrong word for moving on.

## Scope
- When a period reaches zero it stays on screen at `00:00` with the status "Time's up! Press Next to continue"; window title shows "Done – <mode>".
- The **Skip** button is renamed **Next**. Clicking it moves to the next step of the cycle (not started).
- **Start** at that point goes to the next step *and* starts it.
- A finished pomodoro is counted the moment it reaches zero.
- Next/Start/Reset/Skip stop a playing alert. Keyboard: `N` = Next/Skip.

## Acceptance criteria
- [x] Finished period shows 00:00 and the button says Next
- [x] Next follows the cycle (short break, or long break after every N)
- [x] Start after finish advances and starts the next period
- [x] Skip on an unfinished pomodoro still doesn't count it

## Notes
Reset on a finished pomodoro restarts the same pomodoro; it stays counted.

**Changed by [SPEC-008](SPEC-008-next-auto-starts.md):** Next now also starts the next period.
