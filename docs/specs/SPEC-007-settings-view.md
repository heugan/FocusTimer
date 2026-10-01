---
id: SPEC-007
title: Move settings to their own view behind a gear icon
status: Done
priority: Medium
labels: [ui, settings]
created: 2026-10-01
completed: 2026-10-01
adr: [ADR-0006]
---

# SPEC-007: Move settings to their own view behind a gear icon

## Problem
The always-visible settings panel draws attention away from the timer.

## Scope
- Gear icon (⚙) top right of the timer view opens **Settings** in the same window.
- Sections: **Timer** (three durations, long break after N) and **Sound** (sound + Test, volume, length), plus **Defaults**.
- Changes apply immediately; they're saved on **← Back** (or `Esc`) and when the app closes. The old Save button is gone.
- The timer keeps running while settings are open; the window title still shows the time.

## Acceptance criteria
- [x] Timer view contains no settings controls
- [x] Gear opens settings, Back/Esc returns, settings are saved on return
- [x] Timer shortcuts (Space/R/N) are inactive in the settings view
