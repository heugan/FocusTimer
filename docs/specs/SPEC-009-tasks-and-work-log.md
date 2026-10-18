---
id: SPEC-009
title: Current task, pause note and work log (opt-in)
status: Done
priority: High
labels: [logic, ui, settings, log]
created: 2026-10-02
completed: 2026-10-15
adr: [ADR-0002, ADR-0007, ADR-0008]
---

# SPEC-009: Current task, pause note and work log (opt-in)

## Problem
Users want two things from the timer:
1. A **work log** they can use later as input for a report: what they worked on, when and for how long.
2. Help to **find their way back** after a pause or interruption: "where was I?"

Some users only want a plain timer, so the feature must be optional.

## Scope

### Setting (off by default)
- New setting `work_log: bool = False`, shown in the settings view in a new section **WORK LOG** below SOUND:
  - Checkbox **"Tasks and work log"**.
  - Button **"Open log folder"** opens the log folder in Explorer, creating it first if needed.
- **Off:** the app behaves exactly as it does today. No task UI, no pause panel, nothing is written to disk except the existing settings file.
- **On:** everything below is enabled. Switching it off hides the UI and stops logging. Files already written are kept.

### Current task (timer view, only when the feature is on)
- A single-line text field under the status text, with the placeholder **"What are you working on? (optional)"**.
- A **✓** button (tooltip/label "Complete") next to it.
- The text stays in the field between pomodoros, so continuing with the same task takes no clicks.
- A small grey notice under the field reads: **"Don't enter personal data – the log is stored unencrypted in Documents\FocusTimer."**
- All free text follows [SPEC-011](SPEC-011-safe-text-input.md), including the 200-character limit and sanitising.

### Pause note (Pomodoro mode only)
- Clicking **Pause** while a pomodoro is running pauses the timer immediately, as today. An inline panel then appears with:
  - The text field **"Where were you? (optional)"**.
  - **Pause** (also `Enter`): saves the note and closes the panel.
  - `Esc`: closes the panel without a note.
  - The same personal-data notice as above.
  - (SPEC-010 adds a second button, **Switch to…**.)
- After the user resumes, the note is shown as **"↩ You were: <note>"** under the task. It stays visible until the pomodoro is done or stopped.
- The panel does not appear when pausing a break.

### Logging rules
| Event | Logged as |
|---|---|
| Start of a *fresh* pomodoro (not a resume) | `[Pomodoro] <task>` |
| Pause during a pomodoro (written when the panel closes) | `[Pause] <note>` |
| Resume of a paused pomodoro | `[Resume]` |
| Task text changed while a pomodoro is running (committed with `Enter` or by leaving the field, and only if it changed) | `[Switch] <new task>` |
| Pomodoro reaches zero | `[Done] <N> min – <task>` |
| A started pomodoro ended early by Skip, Reset, or changing mode | `[Stopped] <N> min – <task>` (N = minutes actually run, rounded down; paused time excluded) |
| ✓ pressed with a non-empty task (the field is then cleared; the timer is not affected) | `[Complete] <task>` |

- Breaks are not logged.
- An empty task or note just leaves out the text part. For example, `[Pomodoro]` on its own, or `[Done] 25 min`.

### Log format and location ([ADR-0007](../adr/ADR-0007-work-log-format-and-location.md))
- File: `<Documents>\FocusTimer\worklog-YYYY-MM.txt`, one file per calendar month, chosen by the event's timestamp. `<Documents>` is the user's real Documents folder, which may be redirected to OneDrive.
- UTF-8, append-only, one event per line: `YYYY-MM-DD HH:mm [Type] text`, using local time.
- Example:
  ```
  2026-10-02 09:15 [Pomodoro] Issue 123 – review report xyz
  2026-10-02 09:27 [Pause] Section 3, phone call
  2026-10-02 09:31 [Resume]
  2026-10-02 09:44 [Done] 25 min – Issue 123 – review report xyz
  2026-10-02 09:50 [Complete] Issue 123 – review report xyz
  2026-10-02 10:02 [Stopped] 7 min – Issue 456
  ```
- A write error (disk full, folder not writable, file locked) must never crash the app or stop the timer. It is silently ignored; at most a status hint is shown.

### Keyboard
- The `Space`, `R` and `N` shortcuts must not fire while a text field has focus. Typing a space in a task must not start or pause the timer.

### Out of scope
- Parking tasks and returning to them, and keeping the task across restarts. These are in [SPEC-010](SPEC-010-park-and-return.md).
- A report or summary view, a configurable log folder, and a separate "interrupted by" field.

## Acceptance criteria
- [x] With the feature **off** (the default), the timer view looks and works exactly as before, and no log file is created
- [x] An existing settings file without `work_log` loads with the feature off
- [x] Turning it on shows the task field, the ✓ button and the personal-data notice
- [x] "Open log folder" opens `<Documents>\FocusTimer` and creates it if it is missing
- [x] Pausing a running pomodoro shows the pause panel; `Enter` saves the note and `Esc` skips it
- [x] "↩ You were: …" is shown after resuming until the pomodoro is done or stopped
- [x] Every event in the table writes exactly one line in the given format to the correct monthly file
- [x] Done and Stopped report the minutes actually run, with paused time excluded
- [x] A space typed in a text field does not start or pause the timer, and `R`/`N` do nothing there
- [x] A failing log write does not raise an exception and the timer keeps running
- [x] All existing tests still pass

## Test requirements (`test_pomodoro.py`, stdlib `unittest`)
- Log line formatting for every type, with and without text, using an injected clock.
- Month file name taken from the event timestamp, including an event across a month boundary.
- Minutes for Done and Stopped, excluding paused time (use the existing `FakeClock` pattern).
- A write to an unwritable path does not raise.
- `Settings` defaults to `work_log=False`, and older files without the key still load.

## Implementation hints (not prescriptive)
- Keep the logic outside Tk ([ADR-0002](../adr/ADR-0002-logic-ui-separation.md)). Suggested pure classes are a `WorkLog` and the `clean_text()` function from SPEC-011 ([ADR-0008](../adr/ADR-0008-task-state-and-opt-in.md)).
- `pomodoro.py`:
  - `Settings.load` checks `isinstance(default, int)`. **`bool` is a subclass of `int`**, so the new field needs its own check that comes first.
  - The event hooks are in `PomodoroApp.toggle`, `next_step`, `reset`, `select_mode` and `update_loop`, which detects that a pomodoro has finished.
  - The shortcut filter is the `shortcut()` closure in `PomodoroApp.__init__`. Add `tk.Entry` to the widget types it ignores.
  - The timer view is a fixed-size canvas (`WIDTH, HEIGHT = 400, 520`, see [ADR-0005](../adr/ADR-0005-canvas-based-timer-view.md)). Embed widgets with `create_window`. `HEIGHT` may grow to fit the task row.
  - The settings view is built in `_build_settings_view` with the `section()`/`spin()` helpers.
- The real Documents folder can be found with `SHGetKnownFolderPath(FOLDERID_Documents)` through `ctypes`, falling back to `~/Documents`. Open the folder with `os.startfile`.

## Definition of done
Code, tests and docs in one PR: this spec's status set to `Done` and its boxes ticked, the board in `docs/specs/README.md` updated, and the README features and shortcuts updated. Include screenshots of the timer view with the feature on and off, and of the pause panel.
