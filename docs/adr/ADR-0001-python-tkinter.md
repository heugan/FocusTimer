---
id: ADR-0001
title: Python + Tkinter, single file, no dependencies
status: Accepted
date: 2026-09-30
specs: [SPEC-001]
---

# ADR-0001: Python + Tkinter, single file, no dependencies

## Context
A small desktop timer for Windows. Python 3 and the .NET 8 SDK were both available. The owner preferred Python.

## Decision
We will write the app in Python with Tkinter (standard library) in a single module, `pomodoro.py`, with no third-party runtime dependencies. A standalone `.exe` is produced with PyInstaller (`build.ps1`).

## Alternatives considered
- **C# WPF (.NET 8)** — nicer native look and single-file publish, but more ceremony for a tiny app and not the owner's choice.
- **WinForms** — simple but dated look.
- **Electron / web stack** — far too heavy.

## Consequences
- Runs anywhere a full CPython is installed; Windows-specific bits (`winsound`, DPI awareness) are guarded.
- Note: some Pythons lack Tkinter (e.g. the one bundled with Azure CLI). Use the `py` launcher.
- Tkinter widgets are limited visually; see ADR-0005 for how the timer view works around this.
