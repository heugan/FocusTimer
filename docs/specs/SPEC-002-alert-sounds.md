---
id: SPEC-002
title: Selectable alert sounds with configurable length
status: Done
priority: Medium
labels: [sound, settings]
created: 2026-09-30
completed: 2026-09-30
adr: [ADR-0003]
---

# SPEC-002: Selectable alert sounds with configurable length

## Problem
The single Windows system beep is easy to miss and not to everyone's taste.

## Scope
- Three sounds: **Chime** (rising bell arpeggio), **Alarm** (fast harsh beeps), **Digital beep** (watch-style beep-beep).
- Sound plays for a configurable length, default 5 s (1–60).
- Choose and **Test** the sound from settings; Test toggles to **Stop** while playing.
- Choosing a sound previews it.
- Starting the next period stops a playing alert.

## Acceptance criteria
- [x] Each sound plays for exactly the configured length
- [x] Sound choice and length are saved with the other settings
- [x] Defaults restore Chime / 5 s
- [x] First alert after start-up isn't delayed by sound generation
