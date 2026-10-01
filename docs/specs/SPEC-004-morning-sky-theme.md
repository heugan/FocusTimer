---
id: SPEC-004
title: Softer "summer morning sky" theme
status: Done
priority: Medium
labels: [ui]
created: 2026-10-01
completed: 2026-10-01
adr: [ADR-0005]
---

# SPEC-004: Softer "summer morning sky" theme

## Problem
The flat, saturated red/teal/blue backgrounds feel harsh for something you look at all day.

## Scope
- Vertical gradient background, like a clear summer morning sky:
  - **Pomodoro**: sky blue `#8ec5ea` → peach horizon `#fde2c8`, coral accent `#e0745a`
  - **Short break**: aqua `#9fd8df` → mint `#e6f5e9`, teal accent `#2f8f83`
  - **Long break**: lavender `#b7b2ea` → rose `#fbdbe3`, violet accent `#7468c4`
- Dark navy text (`#1f3a5f`) instead of white for readability on light colours.
- White flat buttons; Start/Pause text in the mode's accent colour.
- Active mode tab shown as a soft white pill.

## Acceptance criteria
- [x] Each mode has its own gradient and accent; switching mode recolours immediately
- [x] All text readable on the gradient
- [x] Crisp at high DPI (canvas scaled by screen DPI)
