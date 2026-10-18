---
id: SPEC-011
title: Safe free-text input and personal-data notice
status: Done
priority: High
labels: [security, logic, ui]
created: 2026-10-02
completed: 2026-10-15
adr: [ADR-0007, ADR-0008]
applies_to: [SPEC-009, SPEC-010]
---

# SPEC-011: Safe free-text input and personal-data notice

## Problem
SPEC-009 and SPEC-010 introduce free text that is shown in the UI, stored in `tasks.json` and appended to a log that may later be used for reports. Hostile or accidental input must not break any of these:

- Newlines could forge extra log lines.
- Invisible bidi characters could make the text displayed differ from what is stored.
- Control characters could corrupt the file.
- Very long pastes could break the layout.

Users should also be reminded not to put personal data in an unencrypted log.

## Scope

### One limit for all fields
- **Every** free-text field has a maximum of **200 characters**. This covers the task, "Where were you?" and "New task". Using the same limit everywhere avoids confusing users.
- The entry widget blocks typing past 200 characters. Pasted text is cut to fit.

### `clean_text(text: str, limit: int = 200) -> str`
This is one pure function, used for **all** free text before it is displayed, stored or logged. It is also applied to text loaded from `tasks.json`. Its steps, in order:
1. Unicode normalisation to **NFC**.
2. Convert line and paragraph breaks and tabs to a space: `\r\n`, `\r`, `\n`, `\t`, `\v`, `\f`, U+0085, U+2028 and U+2029.
3. **Remove** all remaining characters in Unicode categories **Cc** (control, e.g. NUL), **Cf** (format, including bidi overrides like U+202E and zero-width characters), **Cs** (surrogates) and **Co** (private use).
4. Replace `|` with `/`. `|` is the field separator in Park and Return log lines.
5. Collapse runs of whitespace into a single space and trim both ends.
6. Truncate to `limit` characters (code points), then trim again.

Letters with diacritics (åäö, é), other scripts and ordinary emoji must be kept unchanged.
Removing Cf characters also removes ZWJ (U+200D), so combined emoji such as 👨‍👩‍👧 may fall apart into separate emoji. This is accepted.

### Handling rules
- Free text is **never** evaluated, used as a format string (`str.format`/`%` with user text as the template), passed to a shell or subprocess, or used in a file name or path. Log file names come only from dates.
- `tasks.json` is written only with `json.dump` (`ensure_ascii=False`).
- The log is written in append mode as UTF-8. Every line starts with a timestamp, so no line can begin with `=`, `+`, `-` or `@` from user input. The raw log is therefore safe to open in a spreadsheet.
- Any **future** export (CSV, HTML, Markdown, report) must escape for its own format. This is recorded in ADR-0007.

### Personal-data notice
- A small grey text appears under the task field and in the pause panel:
  **"Don't enter personal data – the log is stored unencrypted in Documents\FocusTimer."**

### Out of scope
- Encrypting the log, and detecting personal data automatically.

## Acceptance criteria
- [x] No field accepts more than 200 characters, whether typed or pasted
- [x] A task containing a newline produces exactly one log line
- [x] U+202E, NUL and zero-width characters do not reach the screen, `tasks.json` or the log
- [x] `|` in user text is stored and logged as `/`
- [x] åäö, accented letters and emoji are kept
- [x] The personal-data notice is shown under the task field and in the pause panel

## Test requirements (table-driven `unittest`)
| Input | Expected |
|---|---|
| `"a\nb"`, `"a\r\nb"`, `"a\tb"` | `"a b"` |
| `"a\x00b"` | `"ab"` |
| `"abc‮def"` | `"abcdef"` |
| `"a​b"` | `"ab"` |
| `"x | y"` | `"x / y"` |
| `"  many   spaces  "` | `"many spaces"` |
| `"Granska åäö ✅"` | unchanged |
| `"é"` (decomposed é) | `"é"` (NFC) |
| `"a" * 500` | 200 characters |
| `""`, `"   "` | `""` |
| a 199-character string followed by a space and a word | 199 characters, with no trailing space |
