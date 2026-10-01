---
id: SPEC-003
title: Lower default volume and make it a setting
status: Done
priority: High
labels: [sound, settings]
created: 2026-10-01
completed: 2026-10-01
adr: [ADR-0003]
---

# SPEC-003: Lower default volume and make it a setting

## Problem
The alert sounds are too loud.

## Scope
- New setting **Volume (%)**, slider 5–100 in steps of 5.
- 100 % = the loudness used in SPEC-002; default is **50 %** (half the amplitude).
- Releasing the slider previews the sound at the new level; Test uses the current level.

## Acceptance criteria
- [x] Default volume is 50 % and halves the peak amplitude compared with 100 %
- [x] Volume is saved; older settings files without it load with 50 %
- [x] Only the app's own sound is affected (system volume untouched)

## Notes
Implemented by scaling the synthesized samples, see ADR-0003.
