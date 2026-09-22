# Timer-CLI

A very simple Python CLI tool to start a countdown timer.

This fork of [1Blademaster/timer-cli](https://github.com/1Blademaster/timer-cli)
adds an optional bundled alarm sound on macOS. The terminal bell and all existing
defaults are unchanged.

![Example sreenshot](https://raw.githubusercontent.com/1Blademaster/timer-cli/main/images/screenshot.png)

## Installation

### Install this fork on macOS

Requires Python 3.10 or newer and Git. The alarm uses macOS's built-in
`/usr/bin/afplay`; no additional audio library is needed. On each Mac, using
[Homebrew](https://brew.sh/) and [pipx](https://pipx.pypa.io/):

```bash
brew install python pipx git
pipx ensurepath
pipx install --force 'git+https://github.com/migsc/timer-cli.git@main'
```

Open a new terminal after `pipx ensurepath`, then check `timer --version`
(this fork reports `0.1.2+alarm.1`). Re-run the install command to update the
fork. `--force` replaces an existing pipx installation of `timer-cli`.
Installing `timer-cli` directly from PyPI installs upstream without this alarm.
If an older `timer` still runs, use `command -v timer` to check for another
installation earlier on your PATH.

Alternatively, with an existing Python 3.10+ installation:

```bash
python3 -m venv ~/.venvs/timer-cli
~/.venvs/timer-cli/bin/python -m pip install --upgrade 'git+https://github.com/migsc/timer-cli.git@main'
~/.venvs/timer-cli/bin/timer 3s --alarm --no-bell
```

## Usage

```bash
$ timer [options] duration
```

### How to specify a duration

The duration of your timer can be either:
  - A duration string (`__h__m__s`)
  - An absolute datetime (`YYYY-MM-DD`, or `YYYY-MM-DDTHH:MM:SS`)
  - A time only, meaning the next occurrence (`THH:MM:SS`)

#### Duration examples

```bash
timer 1h30m #1hr 30mins
timer 25m #25mins
timer 15m30s #15mins 30secs
timer 2026-01-25T14:00
timer T14:00
```

### Options

#### --no-bell

Supplying the `--no-bell` flag will stop the terminal from "ringing the bell" (making a sound) once the timer has finished.

By default the bell rings immediately at completion and every 10 seconds until
Ctrl+C. This flag only suppresses that terminal bell, including when `--alarm`
is enabled.

#### --alarm (macOS)

Play a bundled 3.6-second pulsing, two-tone alarm immediately at completion and
every 10 seconds thereafter. Playback runs independently of the display, never
overlaps itself, and stops when you press Ctrl+C. The terminal bell remains
enabled unless you also pass `--no-bell`.

```bash
timer 25m --alarm                   # Alarm plus the existing terminal bell
timer 25m --alarm --no-bell         # Alarm only
timer 25m --no-bell                 # Silent, with the existing visual display
timer 3s --alarm --no-bell -m "Test alarm"  # Quick check on each Mac
```

The sound is designed to stand out more than a short terminal bell, but uses
your current audio output and volume; it does not raise system volume, pause
music, or prevent sleep. Test it with your usual music and headphones/speakers
on both Macs. Wait for a repeat, then press Ctrl+C during a pulse to check that
playback stops. Run `timer 3s` and `timer 3s --no-bell` to compare the existing
behavior.

Without `--alarm`, no audio player is required. Requesting it on other platforms,
or when the player or bundled sound is missing, reports an error before the
countdown starts. A launch failure or unsuccessful playback reports an error
and exits; playback exit status is checked at the next 10-second repeat.

The original synthesized sound is freely redistributable under Apache-2.0.
Its [attribution](timer/sounds/ATTRIBUTION.md) and [license](timer/sounds/LICENSE)
are bundled with the installed package. No Apple system sound is redistributed.

#### -m, --message

Use this flag to specify a message to display under the timer. Make sure to surround your string with quotation marks.

```bash
$ timer 1h30m -m "Review the pull requests"
```

#### --font
You can customize the font used to render the timer with 
```bash 
timer --font <font_name> duration
```
Check for available fonts with `timer --list-fonts`

## Contributing

### Development and tests

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . build
python -m unittest discover -v
python -m build
```

Tests cover the sound-option combinations, repeat timing, interruption,
playback errors, and packaged sound/license files. On macOS an additional
smoke test plays the WAV through the real `afplay` at zero volume; audible
quality over music still needs the manual check above. CI tests the built
wheel on Linux and macOS, including Intel and Apple Silicon.

To regenerate the bundled WAV: `python scripts/generate_alarm.py`.

Contributions are always welcome!

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

- Fork the Project
- Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
- Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
- Push to the Branch (`git push origin feature/AmazingFeature`)
- Open a Pull Request

## License

This code is distributed under the [Apache-2.0](https://choosealicense.com/licenses/apache-2.0/) license. See `LICENSE` for more information.
