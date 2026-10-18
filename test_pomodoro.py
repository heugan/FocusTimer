import io
import tempfile
import tkinter as tk
import unittest
import wave
from array import array
from datetime import datetime
from pathlib import Path

from pomodoro import (LONG, POMODORO, SAMPLE_RATE, SHORT, SOUND_NAMES, PomodoroApp, PomodoroSession, Settings,
                      WorkLog, clean_text, format_time, make_wav)


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class RecordingLog:
    def __init__(self):
        self.events = []

    def write(self, event, text=""):
        self.events.append((event, text))
        return True


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.session = PomodoroSession(Settings(), clock=self.clock)

    def run_out(self):
        """Start the current period and let it reach zero."""
        self.session.start()
        self.clock.now += self.session.duration()
        self.assertTrue(self.session.tick())

    def test_counts_down_and_finishes_once(self):
        s = self.session
        s.start()
        self.clock.now += 60
        self.assertAlmostEqual(s.remaining, 24 * 60)
        self.assertFalse(s.tick())
        self.clock.now += 24 * 60
        self.assertTrue(s.tick())
        self.assertFalse(s.tick())
        self.assertFalse(s.running)

    def test_pause_preserves_remaining(self):
        s = self.session
        s.start()
        self.clock.now += 100
        s.pause()
        self.clock.now += 500
        self.assertAlmostEqual(s.remaining, 25 * 60 - 100)
        s.start()
        self.clock.now += 50
        self.assertAlmostEqual(s.remaining, 25 * 60 - 150)

    def test_reset(self):
        s = self.session
        s.start()
        self.clock.now += 300
        s.reset()
        self.assertFalse(s.running)
        self.assertEqual(s.remaining, 25 * 60)

    def test_cycle_order_and_step_index(self):
        s = self.session
        order, indices = [s.mode], [s.cycle_steps()[1]]
        for _ in range(8):
            self.run_out()
            self.assertEqual(s.cycle_steps()[1], indices[-1])  # finished: still on same step
            s.advance()
            order.append(s.mode)
            indices.append(s.cycle_steps()[1])
        self.assertEqual(order, [POMODORO, SHORT, POMODORO, SHORT, POMODORO, SHORT, POMODORO, LONG, POMODORO])
        self.assertEqual(indices, [0, 1, 2, 3, 4, 5, 6, 7, 0])
        self.assertEqual(s.completed_pomodoros, 4)
        self.assertEqual(s.cycle_steps()[0], [POMODORO, SHORT] * 3 + [POMODORO, LONG])

    def test_finished_period_waits_for_next(self):
        s = self.session
        self.run_out()
        self.assertTrue(s.finished)
        self.assertEqual((s.mode, s.completed_pomodoros, s.remaining), (POMODORO, 1, 0))
        s.start()  # nothing left to run
        self.assertFalse(s.running)
        s.advance()
        self.assertFalse(s.finished)
        self.assertEqual((s.mode, s.remaining), (SHORT, 5 * 60))

    def test_skipped_pomodoro_not_counted(self):
        s = self.session
        s.advance()
        self.assertEqual(s.mode, SHORT)
        self.assertEqual(s.completed_pomodoros, 0)

    def test_progress(self):
        s = self.session
        s.start()
        self.clock.now += 5 * 60
        self.assertAlmostEqual(s.progress(), 0.2)

    def test_elapsed_minutes_excludes_paused_time(self):
        s = self.session
        s.start()
        self.clock.now += 125
        s.pause()
        self.clock.now += 600
        self.assertEqual(s.elapsed_minutes(), 2)
        s.start()
        self.clock.now += 60
        self.assertEqual(s.elapsed_minutes(), 3)

    def test_format_time(self):
        self.assertEqual(format_time(1500), "25:00")
        self.assertEqual(format_time(59.2), "01:00")
        self.assertEqual(format_time(0), "00:00")


class SettingsTests(unittest.TestCase):
    def test_roundtrip_and_corrupt_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "settings.json"
            self.assertEqual(Settings.load(path), Settings())  # missing
            Settings(pomodoro_min=50, short_break_min=10).save(path)
            self.assertEqual(Settings.load(path).pomodoro_min, 50)
            path.write_text("{not json", encoding="utf-8")
            self.assertEqual(Settings.load(path), Settings())
            path.write_text('{"pomodoro_min": -3, "long_break_min": "x"}', encoding="utf-8")
            self.assertEqual(Settings.load(path), Settings())
            Settings(sound="alarm", sound_seconds=10, volume=80).save(path)
            loaded = Settings.load(path)
            self.assertEqual((loaded.sound, loaded.sound_seconds, loaded.volume), ("alarm", 10, 80))
            path.write_text('{"pomodoro_min": 30}', encoding="utf-8")  # older file without new keys
            self.assertEqual(Settings.load(path), Settings(pomodoro_min=30))
            path.write_text('{"sound": "trumpet", "sound_seconds": true}', encoding="utf-8")
            self.assertEqual(Settings.load(path), Settings())

    def test_work_log_is_off_by_default_and_loads_from_old_settings(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            path.write_text('{"pomodoro_min": 30}', encoding="utf-8")
            self.assertFalse(Settings.load(path).work_log)
            Settings(work_log=True).save(path)
            self.assertTrue(Settings.load(path).work_log)
            path.write_text('{"work_log": 1}', encoding="utf-8")
            self.assertFalse(Settings.load(path).work_log)


class WorkLogTests(unittest.TestCase):
    def test_uses_event_month_and_one_safe_line(self):
        when = datetime(2026, 2, 28, 23, 59)
        with tempfile.TemporaryDirectory() as d:
            log = WorkLog(Path(d), clock=lambda: when)
            self.assertTrue(log.write("Pomodoro", "Review\nnotes | now"))
            self.assertEqual(
                (Path(d) / "worklog-2026-02.txt").read_text(encoding="utf-8"),
                "2026-02-28 23:59 [Pomodoro] Review notes / now\n",
            )

    def test_formats_events_with_and_without_text(self):
        when = datetime(2026, 3, 1, 8, 5)
        self.assertEqual(WorkLog.format_line("Resume", when=when), "2026-03-01 08:05 [Resume]")
        self.assertEqual(
            WorkLog.format_line("Done", "25 min – Task", when),
            "2026-03-01 08:05 [Done] 25 min – Task",
        )

    def test_write_error_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            blocked = Path(d) / "not-a-folder"
            blocked.write_text("file", encoding="utf-8")
            self.assertFalse(WorkLog(blocked).write("Pause", "note"))

    def test_appends_events_to_the_month_of_each_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            log = WorkLog(Path(d), clock=lambda: datetime(2026, 1, 31, 23, 59))
            log.write("Pause", "=not a spreadsheet formula")
            log.clock = lambda: datetime(2026, 2, 1, 0, 1)
            log.write("Resume")
            self.assertEqual(
                (Path(d) / "worklog-2026-01.txt").read_text(encoding="utf-8"),
                "2026-01-31 23:59 [Pause] =not a spreadsheet formula\n",
            )
            self.assertEqual(
                (Path(d) / "worklog-2026-02.txt").read_text(encoding="utf-8"),
                "2026-02-01 00:01 [Resume]\n",
            )


class CleanTextTests(unittest.TestCase):
    def test_sanitises_free_text(self):
        cases = [
            ("a\nb", "a b"),
            ("a\r\nb", "a b"),
            ("a\tb", "a b"),
            ("a\x00b", "ab"),
            ("abc\u202edef", "abcdef"),
            ("a\u200bb", "ab"),
            ("a\u2066b", "ab"),
            ("a\ue000b", "ab"),
            ("x | y", "x / y"),
            ("  many   spaces  ", "many spaces"),
            ("Granska åäö ✅", "Granska åäö ✅"),
            ("e\u0301", "é"),
            ("", ""),
            ("   ", ""),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(clean_text(source), expected)

    def test_limits_text_without_a_trailing_space(self):
        self.assertEqual(clean_text("a" * 500), "a" * 200)
        self.assertEqual(clean_text("a" * 199 + " word"), "a" * 199)
        self.assertEqual(clean_text("abcdef", limit=5), "abcde")


class WorkLogAppTests(unittest.TestCase):
    """Exercise the event wiring without creating persistent settings or logs."""

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk is unavailable: {error}")
        self.root.withdraw()
        self.app = PomodoroApp(self.root)
        self.clock = FakeClock()
        self.app.settings = Settings(work_log=True)
        self.app.session = PomodoroSession(self.app.settings, clock=self.clock)
        self.log = RecordingLog()
        self.app.work_log = self.log
        self.app._set_task_layout()

    def tearDown(self):
        self.root.destroy()

    def enter_task(self, text):
        self.app.task_focus_in()
        self.app.task_var.set(text)
        self.app.commit_task()

    def test_pause_resume_and_stop_log_active_minutes(self):
        self.enter_task("Write report")
        self.app.toggle()
        self.assertEqual(self.log.events, [("Pomodoro", "Write report")])

        self.clock.now += 125
        self.app.toggle()
        self.assertTrue(self.app.pause_panel_visible)
        self.app.pause_var.set("Section 3")
        self.app.save_pause_note()
        self.assertEqual(self.log.events[-1], ("Pause", "Section 3"))
        self.assertIn("Section 3", self.app.canvas.itemcget(self.app.note_text, "text"))

        self.clock.now += 600  # paused time must not be counted
        self.app.toggle()
        self.clock.now += 60
        self.app.reset()
        self.assertEqual(self.log.events[-2:], [("Resume", ""), ("Stopped", "3 min – Write report")])
        self.assertEqual(self.app.canvas.itemcget(self.app.note_text, "text"), "")

    def test_task_switch_complete_and_opt_out(self):
        self.enter_task("First task")
        self.app.toggle()
        self.app.task_var.set("Second task")
        self.app.commit_task()
        self.app.complete_task()
        self.assertEqual(
            self.log.events,
            [("Pomodoro", "First task"), ("Switch", "Second task"), ("Complete", "Second task")],
        )
        self.assertEqual(self.app._task_text(), "")

        self.app.settings.work_log = False
        self.app.task_focus_in()
        self.app.task_var.set("Ignored task")
        self.app.session.reset()
        self.app.toggle()
        self.assertEqual(len(self.log.events), 3)

    def test_done_and_skip_write_the_correct_single_event(self):
        self.enter_task("Timer task")
        self.app.alert = lambda: None  # the alert itself is not part of log behaviour
        self.app.toggle()
        self.clock.now += self.app.session.duration()
        self.app.update_loop()
        self.assertEqual(self.log.events, [("Pomodoro", "Timer task"), ("Done", "25 min – Timer task")])

        self.app.next_step()  # move to the short break; a completed pomodoro must not be stopped too
        self.assertEqual(len(self.log.events), 2)
        self.app.select_mode(POMODORO)
        self.app.toggle()
        self.clock.now += 90
        self.app.next_step()
        self.assertEqual(self.log.events[-2:], [("Pomodoro", "Timer task"), ("Stopped", "1 min – Timer task")])

    def test_entry_sanitises_and_limits_pasted_text(self):
        self.app.task_focus_in()
        self.app.task_var.set("Two words ")
        self.assertEqual(self.app.task_var.get(), "Two words ")
        self.app.task_var.set("Two words together")
        self.assertEqual(self.app._task_text(), "Two words together")
        self.app.task_var.set("a\n" + "b" * 500)
        self.assertEqual(self.app._task_text(), "a " + "b" * 198)
        self.app.pause_var.set("x | y\u202ez")
        self.assertEqual(self.app.pause_var.get(), "x / yz")

    def test_task_ui_is_hidden_by_default_and_shown_when_enabled(self):
        self.app.settings.work_log = False
        self.app._set_task_layout()
        self.root.update_idletasks()
        self.assertEqual(self.app.canvas.itemcget(self.app.task_window, "state"), "hidden")
        self.assertEqual(self.app.canvas.itemcget(self.app.complete_window, "state"), "hidden")
        self.assertEqual(int(self.app.canvas.cget("height")), self.app.px(520))

        self.app.settings.work_log = True
        self.app._set_task_layout()
        self.root.update_idletasks()
        self.assertEqual(self.app.canvas.itemcget(self.app.task_window, "state"), "normal")
        self.assertEqual(self.app.canvas.itemcget(self.app.complete_window, "state"), "normal")
        self.assertGreater(int(self.app.canvas.cget("height")), self.app.px(520))
        self.assertEqual(self.app.task_var.get(), "What are you working on? (optional)")
        self.assertEqual(
            self.app.canvas.itemcget(self.app.notice_text, "text"),
            "Don't enter personal data – the log is stored unencrypted in Documents\\FocusTimer.",
        )

    def test_pause_panel_shows_its_label_notice_and_state_changes(self):
        self.enter_task("Task")
        self.app.toggle()
        self.clock.now += 10
        self.app.toggle()
        self.root.update_idletasks()
        self.assertTrue(self.app.pause_panel_visible)
        self.assertEqual(self.app.canvas.itemcget(self.app.pause_window, "state"), "normal")
        self.assertEqual(self.app.canvas.itemcget("controls", "state"), "hidden")
        labels = [widget.cget("text") for widget in self.app.pause_panel.winfo_children()
                  if isinstance(widget, tk.Label)]
        self.assertIn("Where were you? (optional)", labels)
        self.assertIn("Don't enter personal data – the log is stored unencrypted in Documents\\FocusTimer.", labels)

        self.app.cancel_pause_panel()
        self.assertFalse(self.app.pause_panel_visible)
        self.assertEqual(self.app.canvas.itemcget(self.app.pause_window, "state"), "hidden")
        self.assertEqual(self.app.canvas.itemcget("controls", "state"), "normal")


class SoundTests(unittest.TestCase):
    def test_every_sound_has_requested_length_and_is_audible(self):
        for name in SOUND_NAMES:
            with self.subTest(name):
                with wave.open(io.BytesIO(make_wav(name, 3))) as w:
                    self.assertEqual(w.getnframes(), 3 * SAMPLE_RATE)
                    self.assertEqual((w.getnchannels(), w.getsampwidth()), (1, 2))
                    frames = w.readframes(w.getnframes())
                self.assertGreater(max(frames[1::2]), 20)  # not silent

    def test_volume_scales_amplitude(self):
        def peak(volume):
            with wave.open(io.BytesIO(make_wav("digital", 1, volume))) as w:
                data = array("h", w.readframes(w.getnframes()))
            return max(abs(x) for x in data)
        self.assertAlmostEqual(peak(50) / peak(100), 0.5, delta=0.01)
        self.assertEqual(Settings().volume, 50)


if __name__ == "__main__":
    unittest.main()
