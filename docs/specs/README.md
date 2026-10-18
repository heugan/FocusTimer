# Specs board

| ID | Title | Status | Priority | Labels | ADRs |
|---|---|---|---|---|---|
| [SPEC-001](SPEC-001-pomodoro-timer.md) | Basic pomodoro timer | Done | High | logic, ui | [0001](../adr/ADR-0001-python-tkinter.md), [0002](../adr/ADR-0002-logic-ui-separation.md), [0004](../adr/ADR-0004-settings-json-in-appdata.md) |
| [SPEC-002](SPEC-002-alert-sounds.md) | Selectable alert sounds with configurable length | Done | Medium | sound, settings | [0003](../adr/ADR-0003-synthesized-sounds.md) |
| [SPEC-003](SPEC-003-volume-setting.md) | Lower default volume and make it a setting | Done | High | sound, settings | [0003](../adr/ADR-0003-synthesized-sounds.md) |
| [SPEC-004](SPEC-004-morning-sky-theme.md) | Softer "summer morning sky" theme | Done | Medium | ui | [0005](../adr/ADR-0005-canvas-based-timer-view.md) |
| [SPEC-005](SPEC-005-next-after-finish.md) | Skip becomes Next when a period ends | Done | Medium | logic, ui | [0002](../adr/ADR-0002-logic-ui-separation.md) |
| [SPEC-006](SPEC-006-session-progress.md) | Show progress through the pomodoro session | Done | Medium | ui | [0005](../adr/ADR-0005-canvas-based-timer-view.md) |
| [SPEC-007](SPEC-007-settings-view.md) | Move settings to their own view behind a gear icon | Done | Medium | ui, settings | [0006](../adr/ADR-0006-settings-as-in-window-view.md) |
| [SPEC-008](SPEC-008-next-auto-starts.md) | Next starts the following period automatically | Done | Medium | logic, ui | |
| [SPEC-009](SPEC-009-tasks-and-work-log.md) | Current task, pause note and work log (opt-in) | Done | High | logic, ui, settings, log | [0007](../adr/ADR-0007-work-log-format-and-location.md), [0008](../adr/ADR-0008-task-state-and-opt-in.md) |
| [SPEC-010](SPEC-010-park-and-return.md) | Switch to another task on interruption, and return to parked tasks | Todo | Medium | logic, ui, log | [0007](../adr/ADR-0007-work-log-format-and-location.md), [0008](../adr/ADR-0008-task-state-and-opt-in.md) |
| [SPEC-011](SPEC-011-safe-text-input.md) | Safe free-text input and personal-data notice | Done | High | security, logic, ui | [0007](../adr/ADR-0007-work-log-format-and-location.md), [0008](../adr/ADR-0008-task-state-and-opt-in.md) |

Suggested order: SPEC-011 → SPEC-009 → SPEC-010.

Next free ID: **SPEC-012**
