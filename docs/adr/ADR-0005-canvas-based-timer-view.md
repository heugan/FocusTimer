---
id: ADR-0005
title: Draw the timer view on a Tk Canvas
status: Accepted
date: 2026-10-01
specs: [SPEC-004, SPEC-006]
---

# ADR-0005: Draw the timer view on a Tk Canvas

## Context
SPEC-004 asks for gradient backgrounds and SPEC-006 for a custom step track and progress bar. Tk `Frame`/`Label` widgets only have solid backgrounds, so text on a gradient would sit in opaque boxes.

## Decision
We will render the whole timer view on one `tk.Canvas`: the gradient as thin horizontal rectangles (redrawn only when the mode changes), text, tabs, step dots and the progress bar as canvas items, and the three buttons as embedded `tk.Button` windows. Canvas coordinates are written in 96-dpi logical pixels and scaled by `winfo_fpixels("1i") / 96`. The view has a fixed size (400 × 520 logical).

## Alternatives considered
- **ttk themes** — still no gradients or transparent labels.
- **Pillow-rendered background image** — adds a dependency (ADR-0001).
- **Third-party toolkit (CustomTkinter, Qt)** — dependency and bigger rewrite.

## Consequences
- Full control over look; easy to add more drawn elements.
- Layout is manual (coordinates), so the window is not resizable.
- Step dots are redrawn every refresh (≈5 Hz, ~20 items) — cheap.
