# Implementation Plan: Macro Recording

**Date**: 2026-07-11
**Spec**: [macro-recording.md](../SPECS/macro-recording.md)

## Summary

Implement the ability to start and stop recording of global mouse clicks and keyboard presses. Captured events are timestamped relative to recording start and stored in memory as an ordered list of `MacroEvent` objects. Uses pynput listeners for global input capture.

## Clean Code Guidelines

All code written for this feature will follow Clean Code principles: meaningful names for variables, functions, and classes that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; consistent error handling with explicit return values or exceptions where appropriate; no magic numbers — all constants extracted to named variables; and the hexagonal architecture layers will be strictly respected so that domain logic never depends on infrastructure details.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: pynput (global input listeners), pywebview (frontend signaling)
- **Storage**: In-memory (macro held in state; persistence handled separately)
- **Testing**: TBD (pytest recommended)
- **Target Platform**: Windows (primary), macOS (best-effort)
- **Project Type**: Desktop app
- **Constraints**: Event timestamps within 50ms accuracy; 10,000+ event capacity

## Project Structure

```text
macro_app/
├── main.py                     # Entry point, wire dependencies
├── domain/
│   └── models.py               # MacroEvent, RecordingSession
├── application/
│   └── recording_service.py    # RecordingService (start/stop/get_events)
├── infrastructure/
│   └── pynput_listener.py      # PynputListener adapter
├── presentation/
│   └── api.py                  # JS API bridge (record_start, record_stop)
├── macros/
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

**Structure Decision**: Lightweight hexagonal architecture. `domain/` holds pure data models with no dependencies. `application/` contains the recording use case logic. `infrastructure/` wraps pynput adapters. `presentation/` exposes the API to the frontend via pywebview's JS bridge.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffold and dependency installation

- [ ] T001 Create project structure per plan (macro_app/ with domain/, application/, infrastructure/, presentation/ subdirectories)
- [ ] T002 Create `requirements.txt` with pynput and pywebview dependencies
- [ ] T003 Create `macro_app/main.py` as the pywebview entry point stub

---

## Phase 2: Domain Models

**Purpose**: Pure data objects — no framework or library dependencies

- [ ] T004 [P] Create `MacroEvent` data class in `domain/models.py` with fields: `event_type` (Literal["mouse_click", "mouse_move", "key_press", "key_release"]), `timestamp` (int, ms), `button` (Optional[str]), `key` (Optional[str]), `x` (Optional[int]), `y` (Optional[int])
- [ ] T005 [P] Create `RecordingSession` data class in `domain/models.py` with fields: `events` (List[MacroEvent]), `start_time` (Optional[float]), `is_recording` (bool)

---

## Phase 3: Infrastructure — Pynput Listener Adapter

**Purpose**: Wrap pynput's global listener API behind a clean interface

- [ ] T006 Implement `PynputListener` class in `infrastructure/pynput_listener.py`: wraps pynput `mouse.Listener` and `keyboard.Listener`
- [ ] T007 Implement `start_listening(callback)` method: begins global mouse and keyboard capture, passes each event to the callback as a `MacroEvent` with relative timestamp (computed from a `start_time` reference clock)
- [ ] T008 Implement `stop_listening()` method: stops both listeners and releases pynput resources
- [ ] T009 Ensure listener threads are properly managed (started/stopped cleanly; no orphan threads)

---

## Phase 4: Application — Recording Service

**Purpose**: Orchestrate the recording use case

- [ ] T010 Implement `RecordingService` class in `application/recording_service.py`; depends on `PynputListener` (injected via constructor)
- [ ] T011 Implement `start_recording()`: creates a new `RecordingSession`, sets `is_recording = True`, stores the start time, and starts the pynput listener; emits a "recording_started" signal to the API layer
- [ ] T012 Implement `stop_recording()`: sets `is_recording = False`, stops the listener, stores the session; emits "recording_stopped" with event count to the API layer
- [ ] T013 Implement `get_current_macro()`: returns the list of recorded `MacroEvent` objects
- [ ] T014 Implement `is_recording` property for state checks
- [ ] T015 Add guard clause: reject `start_recording()` if already recording (return error status)
- [ ] T016 Add guard clause: reject `stop_recording()` if not recording (return error status)

---

## Phase 5: Presentation — Pywebview API Bridge

**Purpose**: Expose recording controls to the frontend JavaScript

- [ ] T017 Implement `record_start()` API function in `presentation/api.py`: calls `RecordingService.start_recording()`, returns result to JS
- [ ] T018 Implement `record_stop()` API function in `presentation/api.py`: calls `RecordingService.stop_recording()`, returns event count to JS
- [ ] T019 Implement `get_macro_events()` API function in `presentation/api.py`: returns the full event list as JSON
- [ ] T020 Register all API functions with pywebview's `js_api` in `main.py`

---

## Phase 6: Integration

**Purpose**: Wire everything together in main.py

- [ ] T021 In `main.py`, instantiate `PynputListener`, inject into `RecordingService`, instantiate the API class, register with `webview.create_window(js_api=...)`
- [ ] T022 Add `__init__.py` files to all packages (domain, application, infrastructure, presentation)

---

## Dependencies & Execution Order

- **Phase 2 (Domain)**: No dependencies — start immediately
- **Phase 3 (Infrastructure)**: Depends on Phase 2 (needs `MacroEvent`)
- **Phase 4 (Application)**: Depends on Phase 2 (models) and Phase 3 (listener)
- **Phase 5 (Presentation)**: Depends on Phase 4 (service)
- **Phase 6 (Integration)**: Depends on all previous phases

Tasks within a phase marked [P] can run in parallel.
