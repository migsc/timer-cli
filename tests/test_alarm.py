import subprocess
import sys
import unittest
from unittest.mock import patch
import wave

from timer.alarm import Alarm, AlarmError, PLAYER_PATH, SOUND_PATH


class AlarmTests(unittest.TestCase):
    def setUp(self):
        self.platform = patch("timer.alarm.sys.platform", "darwin")
        self.access = patch("timer.alarm.os.access", return_value=True)
        self.platform.start()
        self.access.start()
        self.addCleanup(self.platform.stop)
        self.addCleanup(self.access.stop)

    def test_unsupported_platform(self):
        with patch("timer.alarm.sys.platform", "linux"):
            with self.assertRaisesRegex(AlarmError, "requires macOS"):
                Alarm()

    def test_missing_player(self):
        with patch("timer.alarm.os.access", return_value=False):
            with self.assertRaisesRegex(AlarmError, "afplay"):
                Alarm()

    def test_missing_sound(self):
        with patch("timer.alarm.Path.is_file", return_value=False):
            with self.assertRaisesRegex(AlarmError, "Reinstall"):
                Alarm()

    @patch("timer.alarm.subprocess.Popen")
    def test_play_repeats_without_overlap(self, popen):
        process = popen.return_value
        process.poll.side_effect = [None, 0]
        alarm = Alarm()
        alarm.play()
        popen.assert_called_once_with(
            [PLAYER_PATH, str(SOUND_PATH)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True,
        )
        alarm.play()
        self.assertEqual(popen.call_count, 1)
        alarm.play()
        self.assertEqual(popen.call_count, 2)
        process.wait.assert_not_called()

    @patch("timer.alarm.subprocess.Popen", side_effect=OSError("device unavailable"))
    def test_launch_failure(self, popen):
        with self.assertRaisesRegex(AlarmError, "Could not start"):
            Alarm().play()

    @patch("timer.alarm.subprocess.Popen")
    def test_failed_playback_is_reported(self, popen):
        popen.return_value.poll.return_value = 1
        alarm = Alarm()
        alarm.play()
        with self.assertRaisesRegex(AlarmError, "exit status 1"):
            alarm.play()
        self.assertEqual(popen.call_count, 1)

    @patch("timer.alarm.subprocess.Popen")
    def test_stop_terminates_and_reaps_player(self, popen):
        process = popen.return_value
        process.poll.return_value = None
        alarm = Alarm()
        alarm.play()
        alarm.stop()
        alarm.stop()
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=1)

    @patch("timer.alarm.subprocess.Popen")
    def test_stop_kills_unresponsive_player(self, popen):
        process = popen.return_value
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("afplay", 1), 0]
        alarm = Alarm()
        alarm.play()
        alarm.stop()
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)

    @patch("timer.alarm.subprocess.Popen")
    def test_stop_reaps_finished_player(self, popen):
        process = popen.return_value
        process.poll.return_value = 0
        alarm = Alarm()
        alarm.play()
        alarm.stop()
        process.terminate.assert_not_called()
        process.wait.assert_called_once_with(timeout=1)

    def test_stop_before_playback(self):
        Alarm().stop()

    def test_bundled_sound_and_license(self):
        with wave.open(str(SOUND_PATH)) as sound:
            self.assertEqual(sound.getnchannels(), 1)
            self.assertEqual(sound.getsampwidth(), 2)
            self.assertEqual(sound.getframerate(), 44100)
            self.assertAlmostEqual(sound.getnframes() / sound.getframerate(), 3.6)
            self.assertNotEqual(set(sound.readframes(sound.getnframes())), {0})
        self.assertIn("Apache License", SOUND_PATH.with_name("LICENSE").read_text())
        self.assertIn("migsc/timer-cli", SOUND_PATH.with_name("ATTRIBUTION.md").read_text())

    @unittest.skipUnless(sys.platform == "darwin", "Requires the real macOS audio player")
    def test_macos_player_accepts_bundled_sound(self):
        # Muted on CI; audible quality is checked manually on a Mac.
        result = subprocess.run(
            [PLAYER_PATH, "-v", "0", str(SOUND_PATH)],
            capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
