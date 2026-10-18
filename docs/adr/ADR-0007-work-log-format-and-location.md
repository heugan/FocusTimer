---
id: ADR-0007
title: Work log as monthly append-only text files in Documents
status: Accepted
date: 2026-10-02
specs: [SPEC-009, SPEC-010, SPEC-011]
---

# ADR-0007: Work log as monthly append-only text files in Documents

## Context
SPEC-009 introduces a work log. It has two purposes: input for later reports, and a way to find your way back after interruptions. Users need to find and open the file themselves, search it, and copy from it. The app has no third-party dependencies (ADR-0001), and settings already live in the hidden `%APPDATA%\Pomodoro` folder (ADR-0004).

## Decision
We will write the log as **UTF-8 plain-text files, appended to only, with one event per line**, in the format `YYYY-MM-DD HH:mm [Type] text`. Park and Return lines use ` | You were: ` as a separator.

There is **one file per calendar month**, `worklog-YYYY-MM.txt`, stored in **`<Documents>\FocusTimer`**. `<Documents>` is the user's real Documents folder found through the Windows known-folder API, so it follows a redirection to OneDrive. If that fails, the app falls back to `~/Documents`. The settings view has a button that opens the folder.

All user text is sanitised before it is written (SPEC-011), so each event is exactly one line. A write error is ignored and never stops the timer.

## Alternatives considered
- **`%APPDATA%\Pomodoro`** (next to the settings): hidden from users, who would struggle to find it when writing a report.
- **CSV**: easy to import, but the quoting rules are fragile for hand reading. It also carries a risk of formula injection in spreadsheets. An export can be added later.
- **SQLite or JSON Lines**: easier to query, but not readable or editable in Notepad, and more than this needs.
- **`.md`**: lines would merge into paragraphs when rendered.
- **One file per day or one single file**: a file per day gives too many files, and a single file grows without limit. A month matches typical reporting periods.

## Consequences
- Users can read, search and edit the log with any text editor. Reports can be built later by parsing the fixed line format.
- The log is **not encrypted**. This is why the personal-data notice exists (SPEC-011).
- Any future export (CSV, HTML, Markdown, report view) **must escape for its own format**. The raw log is only safe because every line starts with a timestamp and user text is sanitised.
- If a user edits the files by hand, a future parser has to tolerate lines it cannot read and skip them.
