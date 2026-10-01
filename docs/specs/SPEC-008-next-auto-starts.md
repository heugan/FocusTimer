---
id: SPEC-008
title: Next starts the following period automatically
status: Done
priority: Medium
labels: [logic, ui]
created: 2026-10-01
completed: 2026-10-01
adr: []
---

# SPEC-008: Next starts the following period automatically

## Problem
After time's up you had to click **Next** and then **Start** — two clicks to get going again.

## Scope
- Clicking **Next** (shown only after a period has finished) switches to the next step of the cycle **and starts its timer**. Same for the `N` key.
- **Skip** (an unfinished period) is unchanged: it switches step without starting.
- Changes SPEC-005, where Next only switched step.

## Acceptance criteria
- [x] Next after a finished pomodoro starts the break immediately (button shows Pause)
- [x] Next stops the playing alert sound
- [x] Skip during an unfinished period does not start the timer
