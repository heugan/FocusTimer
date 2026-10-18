---
id: SPEC-010
title: Switch to another task on interruption, and return to parked tasks
status: Todo
priority: Medium
labels: [logic, ui, log]
created: 2026-10-02
completed:
adr: [ADR-0007, ADR-0008]
depends_on: [SPEC-009, SPEC-011]
---

# SPEC-010: Switch to another task on interruption, and return to parked tasks

## Problem
Sometimes an interruption means you have to start working on something else: an urgent issue, or a colleague who needs help. You want to switch quickly, but still be able to find your way back to what you were doing. That can be hours or even days later, after the app has been restarted.

## Scope
Everything here applies only when the work log feature ([SPEC-009](SPEC-009-tasks-and-work-log.md)) is on.

### Interruption panel (formerly the pause panel)
- A manual stop during a running Pomodoro is an **interruption**, not a scheduled break. The timer-view control is labelled **Interrupt** and the panel heading is **Interrupted**. **Short break** and **Long break** retain their existing names.
- The panel shows **"Note interruption (optional)"** above the note field, so its purpose is clear.
- It also displays **"Interrupted for <N> min"**, starting at zero when the interruption begins. This is elapsed interruption time, not Pomodoro work time.
- The former **Pause** confirmation control is replaced by an always-available **Resume** action and a **Switch to…** action. Resume returns to the current task and resumes the same Pomodoro with its remaining time.
- Keeping the remaining time after **Resume** is a deliberate FocusTimer adaptation. The canonical Pomodoro Technique treats an unavoidable interruption as a voided Pomodoro and starts a fresh one afterwards; the app instead records the interruption and lets the user return to the work in progress.

### "Switch to…" in the interruption panel
- Clicking **Switch to…** shows a second field, **"New task"**, with a **Switch** button. That confirmation button stays disabled until the user has entered a non-empty target task. `Enter` in that field also confirms.
- On confirm:
  1. The current task and the "Where were you?" note are **parked**. This is skipped if both are empty.
  2. The new task becomes the current task.
  3. **The current pomodoro resumes and keeps running** with the new task. No new pomodoro is started.
  4. The log gets `[Park] <task> | You were: <note>` followed by `[Switch] <new task>`.
- `Esc` cancels Switch to and leaves the Pomodoro interrupted.

### Design question to settle before implementation
The interruption note and the target task must not share an ambiguous meaning. The default design keeps them separate: the first field explains where to resume, and the **New task** field names the task to switch to. If a single field is preferred instead, the label must make clear that its text becomes the new task rather than merely an interruption reason.

### Parked tasks
- Parked tasks form a **stack**, with the most recently parked first. Each entry holds `task`, `note` and `parked_at` (local time, ISO `YYYY-MM-DDTHH:mm`).
- At most **20** parked tasks. Parking a 21st entry drops the oldest.
- The timer view shows one line while the stack is not empty:
  **"↩ Parked: <task> – You were: <note>"**, followed by **"(+N)"** when more are parked. Long text is cut with "…" to fit.
- Clicking the line opens a small list of all parked tasks, showing task, note and how long ago each was parked. Each entry has:
  - **Resume**: the entry becomes the current task and its note is shown as "↩ You were: …". If there was a current task, it is parked first without a note. The log gets `[Return] <task> | You were: <note>`. The timer is not affected.
  - **Remove**: the entry is deleted without a confirmation step. Nothing is logged.
- After **✓ Complete** (SPEC-009), if the stack is not empty, an inline suggestion appears in the timer view (not a modal dialog):
  **"Back to <task>? You were: <note>"** with **Resume** and **Later**. Later hides the suggestion until the next Complete.

### Persistence ([ADR-0008](../adr/ADR-0008-task-state-and-opt-in.md))
- The current task, the current "You were" note and the parked stack are saved to `%APPDATA%\Pomodoro\tasks.json`, using the same folder as `settings.json`. The file is saved after every change and loaded at startup, so it survives restarts.
- Schema:
  ```json
  {
    "version": 1,
    "current": "Issue 789",
    "current_note": "",
    "parked": [
      {"task": "Issue 123 – review report xyz", "note": "Section 3", "parked_at": "2026-10-02T09:27"}
    ]
  }
  ```
- A missing or corrupt file, or invalid entries, fall back to an empty state per field without crashing, the same way `Settings.load` behaves. All loaded text passes through `clean_text()` (SPEC-011).
- When the feature is off, the file is neither read nor written, but it is kept on disk.

### Log lines (added to SPEC-009's table)
```
2026-10-02 09:27 [Park] Issue 123 – review report xyz | You were: section 3
2026-10-02 09:27 [Switch] Urgent issue 789
2026-10-03 08:05 [Return] Issue 123 – review report xyz | You were: section 3
```
When the note is empty, the ` | You were: …` part is left out.

### Out of scope
- Reordering parked tasks, editing parked entries, and searching.

## Acceptance criteria
- [ ] Interrupt, then Switch to with "Issue 789", parks the old task and note and resumes the same pomodoro with the remaining time unchanged
- [ ] The log contains `[Park]` followed by `[Switch]` with the correct text
- [ ] The "↩ Parked" line appears with "(+N)" when more than one task is parked
- [ ] Resume from the list restores the task and note, parks the previous current task, and logs `[Return]`
- [ ] Remove deletes the entry without logging
- [ ] ✓ Complete with parked tasks shows the "Back to …?" suggestion, which Later hides
- [ ] Parked tasks and the current task are still there after restarting the app
- [ ] A corrupt `tasks.json` starts with an empty state and the app does not crash
- [ ] Parking more than 20 tasks drops the oldest

## Test requirements
- Stack order for park and resume, including parking the current task on resume.
- The cap of 20 entries.
- Save/load round trip using a temporary directory.
- A corrupt or invalid file falls back to an empty state.
- Log line format for Park and Return, with and without a note.
- Loaded text is sanitised.
