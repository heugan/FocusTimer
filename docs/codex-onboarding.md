# Codex onboarding

## Runtime

FocusTimer is a Windows desktop application written for Python and Tkinter.
Use a local Python installation that includes Tkinter. Verify the intended
interpreter before changing code:

```powershell
py -c "import sys, tkinter; print(sys.executable); print(tkinter.TkVersion)"
```

The interpreter location is machine-specific. It must stay in local Codex
settings or an approval rule and must never be committed to this repository.

## Automated verification

From the repository root, run:

```powershell
py -m unittest test_pomodoro.py
```

When Codex's sandbox cannot access the local Python installation, approve the
agent's narrowly scoped request to run this test command with that
interpreter. Keep the approval limited to `python -m unittest`; do not grant
unrestricted filesystem access or add a personal interpreter path to project
scripts.

The project uses stdlib `unittest`; add new logic tests to
`test_pomodoro.py`.

## GUI verification

Start the application with the same local interpreter:

```powershell
py pomodoro.py
```

Running a GUI is intentionally a separately approved action because it opens
a visible window outside the normal sandbox. Use it for focused manual checks
of the UI flow requested by a spec, then close the application normally.

## Codex configuration

Keep Codex's normal workspace sandbox and its existing workspace
requirements. Do **not** set a project-specific `default_permissions` profile
or commit `.codex` configuration merely to expose a local Python runtime:
those settings are machine- and runtime-specific and can conflict with
managed workspace requirements.

For a local setup, use Codex's approval flow to save a narrow command rule for
the test command. Keep GUI launches prompted for each run. If the local
interpreter changes, approve the new test command again instead of editing
repository files.

## Scope and safety

- Never commit user names, home-directory paths, interpreter versions, or
  machine-local configuration.
- Do not switch the project to full-access mode just to run Python.
- Treat unit tests as the ordinary automated verification path; use the GUI
  only when a visual check is needed.
