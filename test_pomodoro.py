import io
import tempfile
import unittest
import wave
from array import array
from pathlib import Path

from pomodoro import (LONG, POMODORO, SAMPLE_RATE, SHORT, SOUND_NAMES, PomodoroSession, Settings,
                      format_time, make_wav)


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


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
