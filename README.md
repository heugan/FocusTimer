# FocusTimer
Small Pomodoro like timer to help you keep focused.

A Windows desktop timer for the [Pomodoro Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique),
written in Python with Tkinter (no third-party dependencies).

## Features
- Pomodoro (25 min), Short Break (5 min) and Long Break (15 min) defaults, all adjustable
- Start / Pause, Reset and Skip; when a period ends the timer waits at 00:00 and Skip becomes **Next**
- Automatic cycle: short break after each pomodoro, long break after every 4 (configurable)
- Session card showing the steps of the cycle, the current period's progress and what comes next
- Soft "summer morning sky" gradient per mode
- Alert sound (Chime, Alarm, Digital beep) with a Test button, adjustable volume (default 50 %)
  and length (default 5 s); the window comes to the front when a period ends
- Settings in their own view behind the ⚙ icon, saved to `%APPDATA%\Pomodoro\settings.json`
- Shortcuts: `Space` start/pause, `R` reset, `N` next/skip, `Esc` leave settings

## Run
```
py pomodoro.py
```
(or double-click `pomodoro.pyw` to start without a console window)

## Test
```
py -m unittest test_pomodoro.py
```

## Build a standalone .exe
```
py -m pip install pyinstaller
.\build.ps1
```
The result is `dist\Pomodoro.exe`, runnable on Windows without Python installed.

## Docs
Specs (work items) and Architecture Decision Records live in [`docs/`](docs/README.md).
