---
id: ADR-0006
title: Settings as a view swapped in the main window
status: Accepted
date: 2026-10-01
specs: [SPEC-007]
---

# ADR-0006: Settings as a view swapped in the main window

## Context
SPEC-007 moves settings out of the timer view behind a gear icon. They could open in a separate dialog or replace the timer view in the same window.

## Decision
We will build the settings as a `Frame` of the same size as the timer canvas and swap between the two with `pack`/`pack_forget`. A `view` attribute ("timer"/"settings") gates keyboard shortcuts and canvas rendering. Changes apply immediately; they're persisted when returning to the timer and on close.

## Alternatives considered
- **Modal `Toplevel` dialog** — extra window to position/focus, modal grab blocks the timer UI, awkward on alert (window raise).
- **Explicit Save/Cancel** — more clicks; live apply + save on Back is simpler and Defaults covers "undo all".

## Consequences
- One window, consistent size; the timer keeps running and the title bar still shows the countdown.
- No Cancel: a change can only be undone by changing it back or Defaults.
