"""Pomodoro timer - a small Tkinter desktop app.

Run with:  py pomodoro.py
"""

from __future__ import annotations

import io
import json
import math
import os
import tempfile
import time
import tkinter as tk
import wave
from array import array
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Callable

try:
    import winsound
except ImportError:  # not on Windows
    winsound = None

POMODORO, SHORT, LONG = "pomodoro", "short", "long"
MODE_LABELS = {POMODORO: "Pomodoro", SHORT: "Short Break", LONG: "Long Break"}
MODE_COLORS = {POMODORO: "#ba4949", SHORT: "#38858a", LONG: "#397097"}


def settings_path() -> Path:
    base = os.environ.get("APPDATA") or Path.home()
    return Path(base) / "Pomodoro" / "settings.json"


# --------------------------------------------------------------------------- settings

@dataclass
class Settings:
    pomodoro_min: int = 25
    short_break_min: int = 5
    long_break_min: int = 15
    pomodoros_before_long: int = 4
    sound: str = "chime"
    sound_seconds: int = 5
    volume: int = 50  # percent of full synthesized amplitude

    def minutes_for(self, mode: str) -> int:
        return {POMODORO: self.pomodoro_min,
                SHORT: self.short_break_min,
                LONG: self.long_break_min}[mode]

    @classmethod
    def load(cls, path: Path | None = None) -> "Settings":
        path = path or settings_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            defaults = cls()
            values = {}
            for f in fields(cls):
                default = getattr(defaults, f.name)
                v = data.get(f.name, default)
                if isinstance(default, int):
                    ok = isinstance(v, int) and not isinstance(v, bool) and v >= 1
                else:
                    ok = v in SOUND_NAMES
                values[f.name] = v if ok else default
            return cls(**values)
        except (OSError, ValueError, TypeError, AttributeError):
            return cls()

    def save(self, path: Path | None = None) -> None:
        path = path or settings_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        except OSError:
            pass


# --------------------------------------------------------------------------- sounds

SAMPLE_RATE = 22050


def _bell(buf, start, freq, length, volume):
    """Add a decaying bell tone (fundamental + inharmonic partial) into buf."""
    first = int(start * SAMPLE_RATE)
    for i in range(min(int(length * SAMPLE_RATE), len(buf) - first)):
        t = i / SAMPLE_RATE
        env = math.exp(-4.0 * t)
        buf[first + i] += volume * env * (math.sin(2 * math.pi * freq * t)
                                          + 0.35 * math.sin(2 * math.pi * freq * 2.76 * t))


def _beep(buf, start, freq, length, volume, square=False):
    """Add a steady tone with short fade in/out into buf."""
    first = int(start * SAMPLE_RATE)
    n = min(int(length * SAMPLE_RATE), len(buf) - first)
    fade = int(0.005 * SAMPLE_RATE)
    for i in range(n):
        s = math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
        if square:  # soft-clipped sine: harsh but not ear-piercing
            s = max(-1.0, min(1.0, 3 * s))
        env = min(1.0, i / fade, (n - i) / fade)
        buf[first + i] += volume * env * s


def _chime(buf, seconds):
    # Rising three-note arpeggio (C6-E6-G6), repeated every 1.6 s
    t = 0.0
    while t < seconds:
        for k, f in enumerate((1046.5, 1318.5, 1568.0)):
            _bell(buf, t + k * 0.25, f, 1.5, 0.3)
        t += 1.6


def _alarm(buf, seconds):
    # Four fast harsh beeps, short pause, repeat
    t = 0.0
    while t < seconds:
        for k in range(4):
            _beep(buf, t + k * 0.14, 880, 0.08, 0.35, square=True)
        t += 0.9


def _digital(buf, seconds):
    # Classic watch beep-beep, once per second
    t = 0.0
    while t < seconds:
        _beep(buf, t, 2000, 0.1, 0.4)
        _beep(buf, t + 0.18, 2000, 0.1, 0.4)
        t += 1.0


SOUNDS = {"chime": ("Chime", _chime), "alarm": ("Alarm", _alarm), "digital": ("Digital beep", _digital)}
SOUND_NAMES = tuple(SOUNDS)


def make_wav(name: str, seconds: float, volume: int = 100) -> bytes:
    """Synthesize the named sound as a 16-bit mono WAV of exactly `seconds` length.

    `volume` (0-100) scales the samples; winsound has no volume control of its own."""
    buf = [0.0] * int(seconds * SAMPLE_RATE)
    SOUNDS[name][1](buf, seconds)
    fade = min(len(buf), int(0.1 * SAMPLE_RATE))  # avoid a click if cut mid-tone
    for i in range(fade):
        buf[len(buf) - 1 - i] *= i / fade
    gain = max(0, min(100, volume)) / 100
    samples = array("h", (int(max(-1.0, min(1.0, s * gain)) * 32767) for s in buf))
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(samples.tobytes())
    return out.getvalue()


class SoundPlayer:
    """Plays synthesized sounds asynchronously (winsound can't play from memory async)."""

    def __init__(self):
        self.dir = Path(tempfile.gettempdir()) / "Pomodoro"
        self.cache: dict[tuple[str, int, int], Path] = {}

    def prepare(self, name: str, seconds: int, volume: int) -> Path | None:
        """Generate (once) and return the WAV file for this sound, length and volume."""
        key = (name, seconds, volume)
        path = self.cache.get(key)
        if path is None:
            try:
                self.dir.mkdir(parents=True, exist_ok=True)
                path = self.dir / f"{name}_{seconds}s_{volume}.wav"
                path.write_bytes(make_wav(name, seconds, volume))
            except OSError:
                return None
            self.cache[key] = path
        return path

    def play(self, name: str, seconds: int, volume: int) -> bool:
        if winsound is None:
            return False
        path = self.prepare(name, seconds, volume)
        if path is None:
            return False
        try:
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except RuntimeError:
            return False

    def stop(self) -> None:
        if winsound is not None:
            winsound.PlaySound(None, 0)


# --------------------------------------------------------------------------- logic

class PomodoroSession:
    """Timer and cycle logic, independent of the UI."""

    def __init__(self, settings: Settings, clock: Callable[[], float] = time.monotonic):
        self.settings = settings
        self.clock = clock
        self.mode = POMODORO
        self.completed_pomodoros = 0
        self.running = False
        self.finished = False  # current period ran to zero; waiting for Next
        self._remaining = self.duration()
        self._end = 0.0

    def duration(self, mode: str | None = None) -> float:
        return self.settings.minutes_for(mode or self.mode) * 60

    @property
    def remaining(self) -> float:
        if self.running:
            return max(0.0, self._end - self.clock())
        return self._remaining

    def start(self) -> None:
        if not self.running and self._remaining > 0:
            self._end = self.clock() + self._remaining
            self.running = True

    def pause(self) -> None:
        if self.running:
            self._remaining = self.remaining
            self.running = False

    def reset(self) -> None:
        self.running = False
        self.finished = False
        self._remaining = self.duration()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.reset()

    def next_mode(self) -> str:
        """Mode that follows the current one (after a finished pomodoro has been counted)."""
        if self.mode != POMODORO:
            return POMODORO
        n = self.settings.pomodoros_before_long
        return LONG if self.completed_pomodoros % n == 0 else SHORT

    def advance(self) -> None:
        """Go to the next period: "Next" after a finished period, "Skip" otherwise.

        A skipped pomodoro isn't counted and leads to a short break."""
        if self.finished:
            self.set_mode(self.next_mode())
        elif self.mode == POMODORO:
            self.set_mode(SHORT)
        else:
            self.set_mode(POMODORO)

    def tick(self) -> bool:
        """Return True exactly once when the running period reaches zero."""
        if self.running and self.remaining <= 0:
            self.running = False
            self.finished = True
            self._remaining = 0
            if self.mode == POMODORO:
                self.completed_pomodoros += 1
            return True
        return False

    def progress(self) -> float:
        """Fraction (0-1) of the current period that has elapsed."""
        return 1 - self.remaining / self.duration()

    def cycle_steps(self) -> tuple[list[str], int]:
        """Modes of one full cycle (P S P S ... P L) and the index of the current step."""
        n = self.settings.pomodoros_before_long
        steps = []
        for i in range(n):
            steps += [POMODORO, LONG if i == n - 1 else SHORT]
        done = self.completed_pomodoros
        if self.mode == POMODORO:
            if self.finished:
                done -= 1
            index = 2 * (done % n)
        elif self.mode == LONG:
            index = 2 * n - 1
        else:
            index = 2 * ((done - 1) % n) + 1 if done else 1
            index = min(index, max(1, 2 * n - 3))  # the last break slot is the long one
        return steps, index


def format_time(seconds: float) -> str:
    total = int(seconds + 0.999)  # round up so 0:00 appears only at the very end
    return f"{total // 60:02d}:{total % 60:02d}"


# --------------------------------------------------------------------------- UI

# Morning summer sky: (sky top, horizon, accent). Breaks use related tones.
THEMES = {
    POMODORO: ("#8ec5ea", "#fde2c8", "#e0745a"),
    SHORT: ("#9fd8df", "#e6f5e9", "#2f8f83"),
    LONG: ("#b7b2ea", "#fbdbe3", "#7468c4"),
}
INK, INK_SOFT, PANEL = "#1f3a5f", "#4a6382", "#f6f8fb"
FONT = "Segoe UI"
WIDTH, HEIGHT = 400, 520  # logical pixels at 96 dpi
STATUS = {POMODORO: "Focus", SHORT: "Short break – stretch your legs", LONG: "Long break – well done"}


def _rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


def _blend(c1: str, c2: str, t: float) -> str:
    """Mix two hex colors: t=0 gives c1, t=1 gives c2."""
    return "#%02x%02x%02x" % tuple(round(a + (b - a) * t) for a, b in zip(_rgb(c1), _rgb(c2)))


def _round_rect(x1, y1, x2, y2, r):
    """Points for a rounded rectangle drawn as a smoothed canvas polygon."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


class PomodoroApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = Settings.load()
        self.session = PomodoroSession(self.settings)
        self.player = SoundPlayer()
        self.sound_playing = None  # after-id that clears the "Stop" state
        self.k = root.winfo_fpixels("1i") / 96  # DPI scale for canvas coordinates
        self.view = "timer"
        self._theme_mode = None

        root.title("Pomodoro")
        root.resizable(False, False)
        root.configure(bg=PANEL)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_timer_view()
        self._build_settings_view()
        self.canvas.pack()

        # Focused buttons/inputs handle their own keys; avoid double-triggering
        def shortcut(view, action):
            def handler(e):
                if self.view == view and not isinstance(e.widget, (tk.Button, tk.Spinbox, tk.Scale)):
                    action()
            return handler
        root.bind("<space>", shortcut("timer", self.toggle))
        root.bind("<KeyPress-r>", shortcut("timer", self.reset))
        root.bind("<KeyPress-n>", shortcut("timer", self.next_step))
        root.bind("<Escape>", shortcut("settings", self.show_timer))
        root.bind("<Return>", lambda e: self.apply_settings())

        self.refresh()
        self.update_loop()
        # Generate the alert sound up front so it plays without delay when a period ends
        root.after(300, lambda: self.player.prepare(
            self.settings.sound, self.settings.sound_seconds, self.settings.volume))

    def px(self, v: float) -> int:
        return int(v * self.k)

    # --- timer view
    def _build_timer_view(self):
        px = self.px
        c = self.canvas = tk.Canvas(self.root, width=px(WIDTH), height=px(HEIGHT),
                                    highlightthickness=0, bd=0)

        def clickable(tag, action):
            c.tag_bind(tag, "<Button-1>", lambda e: action())
            c.tag_bind(tag, "<Enter>", lambda e: c.configure(cursor="hand2"))
            c.tag_bind(tag, "<Leave>", lambda e: c.configure(cursor=""))

        # Mode tabs
        self.tabs = {}
        for mode, x in ((POMODORO, 80), (SHORT, 185), (LONG, 290)):
            tag = f"tab_{mode}"
            pill = c.create_polygon(0, 0, 0, 0, smooth=True, fill="", outline="", tags=(tag,))
            text = c.create_text(px(x), px(34), text=MODE_LABELS[mode], fill=INK,
                                 font=(FONT, 10), tags=(tag,))
            x1, y1, x2, y2 = c.bbox(text)
            c.coords(pill, *_round_rect(x1 - px(10), y1 - px(4), x2 + px(10), y2 + px(4), px(12)))
            clickable(tag, lambda m=mode: self.select_mode(m))
            self.tabs[mode] = (pill, text)
        c.create_text(px(WIDTH - 24), px(34), text="⚙", fill=INK, font=(FONT, 16), tags=("gear",))
        clickable("gear", self.show_settings)

        # Time and status
        self.time_text = c.create_text(px(WIDTH / 2), px(125), fill=INK, font=(FONT, 60, "bold"))
        self.status_text = c.create_text(px(WIDTH / 2), px(185), fill=INK_SOFT, font=(FONT, 11))

        # Controls
        btn = dict(font=(FONT, 12, "bold"), width=7, relief="flat", bd=0, pady=5, bg="white",
                   activebackground="#eef2f7", cursor="hand2")
        self.start_button = tk.Button(c, text="Start", command=self.toggle, **btn)
        self.reset_button = tk.Button(c, text="Reset", command=self.reset, fg=INK, **btn)
        self.next_button = tk.Button(c, text="Skip", command=self.next_step, fg=INK, **btn)
        for b, dx in ((self.start_button, -105), (self.reset_button, 0), (self.next_button, 105)):
            c.create_window(px(WIDTH / 2 + dx), px(235), window=b)

        # Session progress card
        self.card = c.create_polygon(*_round_rect(px(20), px(280), px(WIDTH - 20), px(HEIGHT - 20), px(16)),
                                     smooth=True, outline="")
        c.create_text(px(40), px(305), text="Session", anchor="w", fill=INK, font=(FONT, 10, "bold"))
        self.completed_text = c.create_text(px(WIDTH - 40), px(305), anchor="e", fill=INK_SOFT,
                                            font=(FONT, 9))
        self.step_text = c.create_text(px(WIDTH / 2), px(392), fill=INK, font=(FONT, 11, "bold"))
        self.next_text = c.create_text(px(WIDTH / 2), px(414), fill=INK_SOFT, font=(FONT, 9))
        self.bar_bg = c.create_polygon(*_round_rect(px(40), px(440), px(WIDTH - 40), px(450), px(5)),
                                       smooth=True, outline="")
        self.bar = c.create_polygon(0, 0, 0, 0, smooth=True, outline="")
        self.bar_text = c.create_text(px(WIDTH / 2), px(470), fill=INK_SOFT, font=(FONT, 9))

    def _apply_theme(self, mode):
        """Redraw the sky gradient and recolor the card for a mode."""
        c, px = self.canvas, self.px
        top, horizon, accent = THEMES[mode]
        c.delete("sky")
        h, w, step = px(HEIGHT), px(WIDTH), 2
        for y in range(0, h, step):
            color = _blend(top, horizon, y / h)
            c.create_rectangle(0, y, w, y + step, fill=color, outline="", tags=("sky",))
        c.tag_lower("sky")
        self.card_color = _blend(horizon, "#ffffff", 0.6)
        c.itemconfigure(self.card, fill=self.card_color)
        c.itemconfigure(self.bar_bg, fill=_blend(self.card_color, INK, 0.12))
        c.itemconfigure(self.bar, fill=accent)
        self.start_button.configure(fg=accent, activeforeground=accent)
        self._theme_mode = mode

    def _draw_steps(self):
        c, px = self.canvas, self.px
        c.delete("steps")
        steps, current = self.session.cycle_steps()
        y, left, right = px(352), px(50), px(WIDTH - 50)
        gap = (right - left) / max(1, len(steps) - 1)
        upcoming = _blend(self.card_color, INK, 0.15)
        c.create_line(left, y, right, y, fill=upcoming, width=max(1, px(2)), tags=("steps",))
        for i, mode in enumerate(steps):
            x = left + i * gap
            r = min({POMODORO: px(10), SHORT: px(5), LONG: px(8)}[mode], gap * 0.42)
            accent = THEMES[mode][2]
            if i < current or (i == current and self.session.finished):
                fill, outline, width = accent, accent, 1
            elif i == current:
                fill, outline, width = "white", accent, max(2, px(3))
            else:
                fill, outline, width = upcoming, upcoming, 1
            c.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=width,
                          tags=("steps",))

    # --- settings view
    def _build_settings_view(self):
        px = self.px
        f = self.settings_view = tk.Frame(self.root, bg=PANEL, width=px(WIDTH), height=px(HEIGHT))
        f.pack_propagate(False)
        label = dict(bg=PANEL, fg=INK, font=(FONT, 10))

        header = tk.Frame(f, bg=PANEL)
        header.pack(fill="x", padx=12, pady=(12, 6))
        tk.Button(header, text="←  Back", command=self.show_timer, relief="flat", bd=0, bg=PANEL,
                  fg=INK, activebackground="#e6ebf2", font=(FONT, 10), cursor="hand2",
                  padx=6, pady=2).pack(side="left")
        tk.Label(header, text="Settings", bg=PANEL, fg=INK, font=(FONT, 14, "bold")).pack(side="left", padx=10)

        body = tk.Frame(f, bg=PANEL)
        body.pack(fill="x", padx=28)
        body.columnconfigure(0, weight=1)
        self.vars = {}
        row = 0

        def section(title):
            nonlocal row
            tk.Label(body, text=title, bg=PANEL, fg=INK_SOFT, font=(FONT, 9, "bold")).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(14, 4))
            row += 1

        def spin(name, text, maximum):
            nonlocal row
            tk.Label(body, text=text, **label).grid(row=row, column=0, sticky="w", pady=3)
            var = self.vars[name] = tk.IntVar(value=getattr(self.settings, name))
            tk.Spinbox(body, from_=1, to=maximum, width=5, textvariable=var, font=(FONT, 10),
                       command=self.apply_settings).grid(row=row, column=1, sticky="e", pady=3)
            row += 1

        section("TIMER")
        spin("pomodoro_min", "Pomodoro (min)", 120)
        spin("short_break_min", "Short break (min)", 120)
        spin("long_break_min", "Long break (min)", 120)
        spin("pomodoros_before_long", "Long break after (pomodoros)", 12)

        section("SOUND")
        tk.Label(body, text="Sound", **label).grid(row=row, column=0, sticky="w", pady=3)
        sound_row = tk.Frame(body, bg=PANEL)
        sound_row.grid(row=row, column=1, sticky="e", pady=3)
        row += 1
        self.sound_var = tk.StringVar(value=SOUNDS[self.settings.sound][0])
        menu = tk.OptionMenu(sound_row, self.sound_var, *(name for name, _ in SOUNDS.values()),
                             command=lambda _: self.on_sound_changed())
        menu.configure(width=11, font=(FONT, 9), bg="white", relief="flat", highlightthickness=0)
        menu.pack(side="left")
        self.test_button = tk.Button(sound_row, text="▶ Test", width=7, command=self.test_sound,
                                     bg="white", relief="flat", cursor="hand2")
        self.test_button.pack(side="left", padx=(6, 0))

        tk.Label(body, text="Volume (%)", **label).grid(row=row, column=0, sticky="w", pady=3)
        self.vars["volume"] = tk.IntVar(value=self.settings.volume)
        volume = tk.Scale(body, from_=5, to=100, resolution=5, orient="horizontal", length=px(120),
                          variable=self.vars["volume"], command=lambda _: self.apply_settings(),
                          bg=PANEL, fg=INK, highlightthickness=0, troughcolor="#dde3ec", font=(FONT, 8))
        volume.grid(row=row, column=1, sticky="e")
        volume.bind("<ButtonRelease-1>", lambda e: self.play_sound())  # preview new level
        row += 1
        spin("sound_seconds", "Sound length (sec)", 60)

        footer = tk.Frame(f, bg=PANEL)
        footer.pack(side="bottom", fill="x", padx=28, pady=18)
        tk.Label(footer, text="Changes apply immediately and are saved\nwhen you go back.",
                 bg=PANEL, fg=INK_SOFT, font=(FONT, 8), justify="left").pack(side="left")
        tk.Button(footer, text="Defaults", width=9, command=self.restore_defaults, bg="white",
                  relief="flat", cursor="hand2").pack(side="right")

    def show_settings(self):
        self.canvas.pack_forget()
        self.settings_view.pack()
        self.view = "settings"

    def show_timer(self):
        self.apply_settings()
        self.settings.save()
        self.settings_view.pack_forget()
        self.canvas.pack()
        self.view = "timer"
        self.refresh()

    # --- actions
    def toggle(self):
        self.stop_sound()
        if self.session.running:
            self.session.pause()
        else:
            if self.session.finished:  # Start after time's up goes straight to the next period
                self.session.advance()
            self.session.start()
        self.refresh()

    def reset(self):
        self.stop_sound()
        self.session.reset()
        self.refresh()

    def next_step(self):
        self.stop_sound()
        finished = self.session.finished
        self.session.advance()
        if finished:  # Next (after time's up) starts the following period right away; Skip doesn't
            self.session.start()
        self.refresh()

    def select_mode(self, mode):
        self.stop_sound()
        self.session.set_mode(mode)
        self.refresh()

    def read_settings(self) -> Settings | None:
        try:
            values = {k: int(v.get()) for k, v in self.vars.items()}
        except (tk.TclError, ValueError):
            return None
        if any(v < 1 for v in values.values()):
            return None
        sound = next(k for k, (label, _) in SOUNDS.items() if label == self.sound_var.get())
        return Settings(sound=sound, **values)

    def apply_settings(self):
        new = self.read_settings()
        if new is None or new == self.settings:
            return
        old_duration = self.session.duration()
        for f in fields(Settings):
            setattr(self.settings, f.name, getattr(new, f.name))
        # Show a new duration right away if the timer hasn't been started in this period
        s = self.session
        if not s.running and not s.finished and s.remaining == old_duration:
            s.reset()
        self.refresh()

    def restore_defaults(self):
        defaults = Settings()
        for name, var in self.vars.items():
            var.set(getattr(defaults, name))
        self.sound_var.set(SOUNDS[defaults.sound][0])
        self.apply_settings()

    def on_close(self):
        self.stop_sound()
        self.apply_settings()
        self.settings.save()
        self.root.destroy()

    # --- sound
    def play_sound(self) -> bool:
        self.stop_sound()
        st = self.settings
        if not self.player.play(st.sound, st.sound_seconds, st.volume):
            return False
        self.test_button.configure(text="■ Stop")
        self.sound_playing = self.root.after(st.sound_seconds * 1000, self._sound_finished)
        return True

    def _sound_finished(self):
        self.sound_playing = None
        self.test_button.configure(text="▶ Test")

    def stop_sound(self):
        if self.sound_playing is not None:
            self.root.after_cancel(self.sound_playing)
            self.player.stop()
            self._sound_finished()

    def test_sound(self):
        if self.sound_playing is not None:
            self.stop_sound()
        else:
            self.apply_settings()
            if not self.play_sound():
                self.root.bell()

    def on_sound_changed(self):
        self.apply_settings()
        self.play_sound()  # preview the newly selected sound

    # --- loop & rendering
    def update_loop(self):
        if self.session.tick():
            self.alert()
        self.refresh()
        self.root.after(200, self.update_loop)

    def alert(self):
        if not self.play_sound():
            self.root.bell()
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(1500, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def refresh(self):
        s, c, px = self.session, self.canvas, self.px
        label = MODE_LABELS[s.mode]
        time_str = format_time(s.remaining)
        self.root.title(f"Done – {label}" if s.finished else f"{time_str} – {label}")
        if self.view != "timer":
            return
        if self._theme_mode != s.mode:
            self._apply_theme(s.mode)
        top, _, accent = THEMES[s.mode]

        for mode, (pill, text) in self.tabs.items():
            active = mode == s.mode
            c.itemconfigure(pill, fill=_blend(top, "#ffffff", 0.55) if active else "")
            c.itemconfigure(text, font=(FONT, 10, "bold" if active else "normal"))

        c.itemconfigure(self.time_text, text=time_str)
        if s.finished:
            status = "Time's up! Press Next to continue"
        elif s.running:
            status = STATUS[s.mode]
        elif s.remaining < s.duration():
            status = "Paused"
        else:
            status = "Ready when you are"
        c.itemconfigure(self.status_text, text=status)
        self.start_button.configure(text="Pause" if s.running else "Start")
        self.next_button.configure(text="Next" if s.finished else "Skip")

        # Session progress
        n = self.settings.pomodoros_before_long
        steps, index = s.cycle_steps()
        c.itemconfigure(self.completed_text, text=f"Pomodoros completed: {s.completed_pomodoros}")
        if s.mode == POMODORO:
            c.itemconfigure(self.step_text, text=f"Pomodoro {index // 2 + 1} of {n}")
        else:
            c.itemconfigure(self.step_text, text=label)
        upcoming = s.next_mode() if s.finished or s.mode != POMODORO else (
            LONG if (s.completed_pomodoros + 1) % n == 0 else SHORT)
        c.itemconfigure(self.next_text, text=f"Next: {MODE_LABELS[upcoming]}")
        self._draw_steps()

        x1, x2 = px(40), px(WIDTH - 40)
        fill_to = x1 + (x2 - x1) * s.progress()
        if fill_to - x1 < px(2):
            c.coords(self.bar, 0, 0, 0, 0)
        else:
            c.coords(self.bar, *_round_rect(x1, px(440), fill_to, px(450), px(5)))
        total = s.duration() / 60
        elapsed = total - s.remaining / 60
        c.itemconfigure(self.bar_text, text=f"{int(elapsed)} of {int(total)} min · {int(s.progress() * 100)}%")


def main():
    try:  # crisp text on high-DPI Windows displays
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
