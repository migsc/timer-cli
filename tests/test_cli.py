import unittest
from unittest.mock import patch

from click.testing import CliRunner

from timer.__main__ import main
from timer.alarm import AlarmError


class CliTests(unittest.TestCase):
    def test_completion_sound_combinations(self):
        for flags, bell_count, alarm_count in (
            ([], 2, 0),
            (["--no-bell"], 0, 0),
            (["--alarm"], 2, 2),
            (["--alarm", "--no-bell"], 0, 2),
        ):
            with self.subTest(flags=flags), \
                    patch("timer.__main__.Alarm") as alarm, \
                    patch("timer.__main__.Console.bell") as bell, \
                    patch("timer.__main__.time.time", side_effect=[100, 102]), \
                    patch("timer.__main__.time.sleep", side_effect=[None, None, KeyboardInterrupt]) as sleep:
                result = CliRunner().invoke(main, ["1s", *flags])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("Quitting", result.output)
                self.assertEqual(bell.call_count, bell_count)
                self.assertEqual(alarm.return_value.play.call_count, alarm_count)
                self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 10, 10])
                if alarm_count:
                    alarm.return_value.stop.assert_called_once()
                else:
                    alarm.assert_not_called()

    @patch("timer.__main__.Alarm", side_effect=AlarmError("--alarm requires macOS"))
    @patch("timer.__main__.time.sleep")
    def test_unavailable_alarm_fails_before_countdown(self, sleep, alarm):
        result = CliRunner().invoke(main, ["1s", "--alarm"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("requires macOS", result.output)
        sleep.assert_not_called()

    @patch("timer.__main__.Alarm")
    @patch("timer.__main__.time.sleep", side_effect=KeyboardInterrupt)
    def test_interrupt_during_countdown_does_not_play(self, sleep, alarm):
        result = CliRunner().invoke(main, ["25m", "--alarm"])
        self.assertEqual(result.exit_code, 0, result.output)
        alarm.return_value.play.assert_not_called()
        alarm.return_value.stop.assert_called_once()

    @patch("timer.__main__.Alarm")
    @patch("timer.__main__.time.time", side_effect=[100, 102])
    @patch("timer.__main__.time.sleep")
    def test_playback_failure_exits_cleanly(self, sleep, time, alarm):
        alarm.return_value.play.side_effect = AlarmError("Alarm playback failed")
        result = CliRunner().invoke(main, ["1s", "--alarm", "--no-bell"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: Alarm playback failed", result.output)
        alarm.return_value.stop.assert_called_once()

    @patch("timer.__main__.Alarm")
    def test_help_describes_opt_in_alarm_without_initializing_player(self, alarm):
        result = CliRunner().invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--alarm", result.output)
        self.assertIn("macOS only", result.output)
        alarm.assert_not_called()

    @patch("timer.__main__.Alarm")
    def test_invalid_duration_does_not_initialize_player(self, alarm):
        result = CliRunner().invoke(main, ["nonsense", "--alarm"])
        self.assertEqual(result.exit_code, 1)
        alarm.assert_not_called()
