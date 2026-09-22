"""Generate the original timer-cli alarm; no third-party recordings or samples.

Copyright 2026 timer-cli fork contributors
SPDX-License-Identifier: Apache-2.0
"""

import math
from pathlib import Path
import struct
import wave


SAMPLE_RATE = 44100


def generate(path: Path) -> None:
    # Three pairs of alternating tones with short gaps: 3.6 seconds total.
    # Smooth attacks/releases avoid clicks; harmonics add presence over music.
    frames = bytearray()
    for pulse in range(6):
        frequency = 880 if pulse % 2 == 0 else 1320
        for sample in range(int(SAMPLE_RATE * 0.6)):
            t = sample / SAMPLE_RATE
            envelope = max(0.0, min(1.0, t / 0.015, (0.4 - t) / 0.04))
            phase = 2 * math.pi * frequency * t
            tone = (math.sin(phase) + 0.3 * math.sin(2 * phase)) / 1.3
            frames.extend(struct.pack("<h", round(32767 * 0.8 * envelope * tone)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as sound:
        sound.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
        sound.writeframes(frames)


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "timer" / "sounds" / "alarm.wav")
