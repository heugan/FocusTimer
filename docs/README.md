# Project docs

Lightweight work tracking in plain Markdown, modelled loosely on Linear / Azure DevOps.

| Folder | What | Comparable to |
|---|---|---|
| [`specs/`](specs/README.md) | One file per piece of work: problem, scope, acceptance criteria, status | Linear issue / ADO user story |
| [`adr/`](adr/README.md) | Architecture Decision Records: one file per significant technical decision | ADO wiki decision log |

## Specs

- **ID**: `SPEC-NNN`, never reused. File name `SPEC-NNN-short-slug.md`.
- **Status** (in front matter): `Backlog` → `Todo` → `In Progress` → `In Review` → `Done` (or `Canceled`).
- **Priority**: `Urgent`, `High`, `Medium`, `Low`.
- **Labels**: free-form, e.g. `ui`, `sound`, `settings`, `logic`.
- Acceptance criteria are checkboxes; tick them as they are verified.
- When status changes, update both the file and the board in [`specs/README.md`](specs/README.md).
- Start from [`specs/_template.md`](specs/_template.md).

## ADRs

- **ID**: `ADR-NNNN`, file name `ADR-NNNN-short-slug.md`, format after Michael Nygard.
- **Status**: `Proposed`, `Accepted`, `Deprecated`, `Superseded by ADR-NNNN`.
- ADRs are not edited after acceptance except for status; a changed decision gets a new ADR that supersedes the old one.
- Specs link the ADRs they rely on, and ADRs link the spec that prompted them.
- Start from [`adr/_template.md`](adr/_template.md).
