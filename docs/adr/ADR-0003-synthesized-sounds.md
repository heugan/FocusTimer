---
id: ADR-0003
title: Synthesize alert sounds in code and play them from temp WAV files
status: Accepted
date: 2026-09-30
specs: [SPEC-002, SPEC-003]
---

# ADR-0003: Synthesize alert sounds in code and play them from temp WAV files

## Context
We need several alert sounds with an exact, configurable length and an adjustable volume, without third-party audio libraries (ADR-0001) and without shipping licensed audio files. Standard-library `winsound` can only play WAV files/aliases, has no volume control, and cannot play from memory asynchronously.

## Decision
We will generate each sound with simple synthesis (`make_wav(name, seconds, volume)`: bell partials, soft-clipped beeps), scale the samples by the volume setting, and write the result to `%TEMP%\Pomodoro\<sound>_<seconds>s_<volume>.wav`. Files are cached per (sound, length, volume) and played with `SND_FILENAME | SND_ASYNC`; `PlaySound(None, 0)` stops playback. The configured sound is pre-generated at start-up.

## Alternatives considered
- **Bundled WAV/MP3 files** — fixed length, licensing, extra files for PyInstaller.
- **`pygame` / `simpleaudio`** — real volume control and mixing, but third-party dependencies.
- **Change volume via the Windows mixer (`waveOutSetVolume`)** — affects the whole app session and is platform plumbing we don't need.

## Consequences
- Sounds are fully reproducible from code and testable (length, non-silence, amplitude scaling).
- Generating a long chime takes ~1 s the first time; pre-generation hides this for the alert itself.
- A few small WAV files accumulate in `%TEMP%\Pomodoro` (harmless; OS cleans temp).
