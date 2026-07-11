# Easy Macro Recorder

A lightweight desktop macro recorder for single-player games. Automate repetitive actions and grind XP without being glued to your keyboard.

![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-blue)
![Tests](https://img.shields.io/badge/tests-64%20passing-brightgreen)

## Features

- **Record** mouse clicks, movements, and keyboard presses with accurate relative timestamps
- **Playback** recorded macros with configurable loop count (including infinite) and delay between loops
- **Save/Load** macros as `.json` files — reuse them across sessions
- **Edit** macros after recording: delete events, adjust timing, insert new events or delays
- **Global hotkeys** — control recording/playback while in-game without alt-tabbing (F6/F7/F8, configurable)
- **Emergency stop** (F8) to instantly halt any running macro

## Quick Start

### Option 1: Download pre-built binary

Download the latest release for your platform from [Releases](https://github.com/LJSaumeth/EASY_MACRO_RECORDER/releases):

**Linux (x64):**
```bash
tar xzf EasyMacroRecorder-linux-x64.tar.gz
cd EasyMacroRecorder
./EasyMacroRecorder
```

**Windows (x64):**
```
1. Download EasyMacroRecorder-windows-x64.zip
2. Extract the .zip
3. Double-click EasyMacroRecorder.exe
```

### Option 2: Install from source

#### Linux (automated)

```bash
git clone https://github.com/LJSaumeth/EASY_MACRO_RECORDER.git
cd EASY_MACRO_RECORDER
./setup.sh    # Detects distro and installs all dependencies
./run.sh      # Launches the app (auto-detects Wayland/X11)
```

Supported distros: **Ubuntu**, **Debian**, **Fedora**, **Arch**, **Zorin OS**, and derivatives.

<details>
<summary>Manual installation (Linux)</summary>

```bash
# Install system dependencies
# Debian/Ubuntu:
sudo apt install python3-gi gir1.2-webkit2-4.1 python3-xlib
# Fedora:
sudo dnf install python3-gobject webkit2gtk4.1 python3-xlib
# Arch:
sudo pacman -S python-gobject webkit2gtk-4.1 python-xlib

# Install Python dependencies and run
pip install -r macro_app/requirements.txt
cd macro_app
python main.py
```
</details>

#### Windows (manual)

Requires Python 3.10+ and pip:

```bash
git clone https://github.com/LJSaumeth/EASY_MACRO_RECORDER.git
cd EASY_MACRO_RECORDER
pip install -r macro_app/requirements.txt
cd macro_app
python main.py
```

No additional system packages needed — pynput and pywebview work out of the box on Windows.

### Build standalone executable

```bash
cd macro_app
pyinstaller EasyMacroRecorder.spec           # Windows → dist/EasyMacroRecorder/EasyMacroRecorder.exe
pyinstaller EasyMacroRecorder-linux.spec     # Linux → dist/EasyMacroRecorder/EasyMacroRecorder
```

## Usage

1. Launch the app (run as **administrator** on Windows / **root** on Linux for full game compatibility)
2. Press **F6** to start recording, perform your game actions
3. Press **F6** again to stop recording
4. Press **F7** to play back the macro
5. Press **F8** at any time for emergency stop
6. Save your macro with a name to reuse it later

Configure loop count and delay in the Playback panel. Edit events in the Event Editor panel.

> **Linux / Wayland**: Global hotkeys work through XWayland. For gaming, consider running games in X11 mode or use [gamescope](https://github.com/ValveSoftware/gamescope).

## Tech Stack

- **Backend**: Python + pynput (input capture/injection) + pywebview (desktop window)
- **Frontend**: Vanilla HTML, CSS, JavaScript — no frameworks, no build step
- **Architecture**: Hexagonal (ports & adapters), Clean Code
- **Tests**: pytest — 64 unit tests across all layers

## Project Structure

```
EASY_MACRO_RECORDER/
├── setup.sh                  # Multi-distro Linux installer
├── run.sh                    # Wayland-aware launcher
├── UPLAN.md                  # Upgrade plan document
├── tests/                    # Test suite (64 tests)
│   ├── domain/               # Model tests
│   ├── application/          # Service tests
│   ├── infrastructure/       # Storage tests
│   └── presentation/         # API tests
└── macro_app/
    ├── main.py               # Entry point — wires deps, Linux checks
    ├── domain/               # Pure data models (MacroEvent, Macro, HotkeyBinding)
    ├── application/          # Use cases (recording, playback, persistence, editing)
    ├── infrastructure/       # Adapters (pynput, JSON file storage)
    ├── presentation/         # JS API bridge (MacroApi)
    ├── frontend/             # HTML, CSS, JS UI (6 panels)
    ├── macros/               # Saved .json macro files
    └── EasyMacroRecorder.spec          # PyInstaller spec (Windows)
    └── EasyMacroRecorder-linux.spec    # PyInstaller spec (Linux)
```

## Development

```bash
# Install dev dependencies
pip install -r macro_app/requirements.txt
pip install pytest

# Run tests
pytest tests/ -v

# Run from source
cd macro_app
python main.py
```

## License

MIT — Luis Saumeth
