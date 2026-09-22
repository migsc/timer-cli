"""Optional macOS playback for the bundled completion alarm."""

import os
from pathlib import Path
import subprocess
import sys
from typing import Optional


SOUND_PATH = Path(__file__).resolve().parent / "sounds" / "alarm.wav"
PLAYER_PATH = "/usr/bin/afplay"


class AlarmError(Exception):
    """The requested alarm cannot be played."""


class Alarm:
    def __init__(self) -> None:
        if sys.platform != "darwin":
            raise AlarmError("--alarm requires macOS. Omit --alarm to use the terminal bell.")
        if not os.access(PLAYER_PATH, os.X_OK):
            raise AlarmError("--alarm requires macOS's /usr/bin/afplay, which is unavailable.")
        if not SOUND_PATH.is_file():
            raise AlarmError("The bundled alarm sound is missing. Reinstall timer-cli.")
        self._process: Optional[subprocess.Popen] = None

    def play(self) -> None:
        if self._process is not None:
            status = self._process.poll()
            if status is None:
                return  # Never overlap playback, even if the audio device stalls.
            if status != 0:
                raise AlarmError(f"Alarm playback failed (afplay exit status {status}).")
        try:
            self._process = subprocess.Popen(
                [PLAYER_PATH, str(SOUND_PATH)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            raise AlarmError(f"Could not start alarm playback: {exc}") from exc

    def stop(self) -> None:
        if self._process is None:
            return
        if self._process.poll() is None:
            self._process.terminate()
        try:
            self._process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()
        self._process = None
