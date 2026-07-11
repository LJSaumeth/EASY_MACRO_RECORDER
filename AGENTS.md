# AGENTS.md

## Project

- **Easy Macro Recorder** — a desktop macro recorder for single-player games (grinding XP).
- Python backend, HTML/CSS/JS frontend, rendered via pywebview.
- MIT License, author Luis Saumeth.
- Follow Clean Code guidelines throughout.
- Use hexagonal architecture where practical. Keep it lightweight.

## Architecture

```
macro_app/
├── main.py              # Entrypoint — wires all dependencies, starts pywebview
├── domain/
│   ├── models.py        # MacroEvent, RecordingSession, PlaybackSession, Macro, HotkeyBindings
│   └── exceptions.py    # MacroError hierarchy
├── application/
│   ├── recording_service.py
│   ├── playback_service.py
│   ├── persistence_service.py
│   ├── hotkey_service.py
│   └── macro_editor.py
├── infrastructure/
│   ├── pynput_listener.py    # Global input capture + hotkey listener
│   ├── pynput_controller.py  # Input injection (mouse/keyboard)
│   ├── json_file_storage.py  # Atomic .json save/load with schema validation
│   └── hotkey_config_store.py
├── presentation/
│   └── api.py           # MacroApi — 20 methods exposed to JS via pywebview
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── macros/              # .json macro files stored here (auto-created at startup)
```

## Dependencies

- **Python**: `pynput` (input capture/injection), `pywebview` (desktop window + JS bridge), `json` (stdlib)
- **Frontend**: vanilla HTML, CSS, JavaScript — no frameworks, no build step.
- Install: `pip install -r macro_app/requirements.txt`

## Commands

- **Run**: `cd macro_app && python main.py`
- **Build exe**: `cd macro_app && pyinstaller EasyMacroRecorder.spec` (output in `macro_app/dist/EasyMacroRecorder/`)
- No linter, formatter, type checker, or test framework configured yet.

## Development Phases

1. Backend specs — **done** (5 specs in `DOCS/SPECS/`)
2. Backend plans — **done** (5 plans in `DOCS/PLANS/`)
3. Backend implementation — **done** (hexagonal layers in `macro_app/`)
4. Frontend specs — **done** (6 specs, prefixed `frontend-*`)
5. Frontend plans — **done** (6 plans, prefixed `frontend-*`)
6. Frontend implementation — **pending**

One feature = one spec + one plan. Templates at `DOCS/SPECS/spec-template.md` and `DOCS/PLANS/plan-template.md`.

## Key Conventions

- **Hexagonal layers**: `domain` → `application` → `infrastructure` → `presentation`. Domain never imports from outer layers. Services receive their dependencies via constructor injection.
- **Frontend-backend bridge**: JS calls `window.pywebview.api.methodName()`. The `MacroApi` class in `presentation/api.py` defines all callable methods. No HTTP server — direct Python↔JS calls.
- **State polling**: Frontend polls `get_app_state()` every 500ms. All panels receive state via their `updateState(state)` callback from the `AppController` polling loop.
- **Hotkey lifecycle**: `HotkeyService.initialize()` must be called on startup (done in `build_services()`), and `shutdown()` on exit (done in `main()` finally block).
- **Global hotkeys**: F6 = record toggle, F7 = playback toggle, F8 = emergency stop. Config persisted in `macros/.hotkey_config.json`.
- **Macro files**: Saved as `.json` in `macros/`. Directory auto-created by `JsonFileStorage`. Atomic writes (temp file + rename). Filenames sanitized to `[a-zA-Z0-9\-_]`.
- **Import style**: Absolute imports from `macro_app/` root (e.g., `from domain.models import MacroEvent`). Run from within `macro_app/`.
