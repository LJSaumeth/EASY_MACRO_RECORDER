# Easy Macro Recorder

A lightweight desktop macro recorder for single-player games. Automate repetitive actions and grind XP without being glued to your keyboard.

## Features

- **Record** mouse clicks, movements, and keyboard presses with accurate relative timestamps
- **Playback** recorded macros with configurable loop count (including infinite) and delay between loops
- **Save/Load** macros as `.json` files — reuse them across sessions
- **Edit** macros after recording: delete events, adjust timing, insert new events or delays
- **Global hotkeys** — control recording/playback while in-game without alt-tabbing (F6/F7/F8, configurable)
- **Emergency stop** (F8) to instantly halt any running macro

## Tech Stack

- **Backend**: Python + pynput (input capture/injection) + pywebview (desktop window)
- **Frontend**: Vanilla HTML, CSS, JavaScript — no frameworks, no build step
- **Architecture**: Hexagonal (ports & adapters), Clean Code

## Quick Start

### Run from source

```bash
pip install -r macro_app/requirements.txt
cd macro_app
python main.py
```

### Build standalone executable

```bash
pip install -r macro_app/requirements.txt
cd macro_app
pyinstaller EasyMacroRecorder.spec
# Output: dist/EasyMacroRecorder/EasyMacroRecorder.exe
```

## Usage

1. Launch the app (run as administrator for full game compatibility)
2. Press **F6** to start recording, perform your game actions
3. Press **F6** again to stop recording
4. Press **F7** to play back the macro
5. Press **F8** at any time for emergency stop
6. Save your macro with a name to reuse it later

Configure loop count and delay in the Playback panel. Edit events in the Event Editor panel.

## Project Structure

```
macro_app/
├── main.py              # Entry point — wires dependencies, starts pywebview
├── domain/              # Pure data models (MacroEvent, Macro, HotkeyBinding)
├── application/         # Use cases (recording, playback, persistence, editing, hotkeys)
├── infrastructure/       # Adapters (pynput, JSON file storage)
├── presentation/         # JS API bridge (20 methods)
├── frontend/             # HTML, CSS, JS UI
└── macros/               # Saved .json macro files
```

## License

MIT — Luis Saumeth
