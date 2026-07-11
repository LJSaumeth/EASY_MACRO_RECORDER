# Implementation Plan: Macro Playback

**Date**: 2026-07-11
**Spec**: [macro-playback.md](../SPECS/macro-playback.md)

## Summary

Implement the ability to replay a recorded macro by injecting mouse and keyboard events at the OS level using pynput controllers. Supports configurable loop count (1 to N, plus infinite) and configurable delay between iterations. Playback can be stopped at any time. Timing between events is preserved from the original recording.

## Clean Code Guidelines

All code written for this feature will follow Clean Code principles: meaningful names for variables, functions, and classes that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; consistent error handling with explicit return values or exceptions where appropriate; no magic numbers — all constants extracted to named variables; and the hexagonal architecture layers will be strictly respected so that domain logic never depends on infrastructure details.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: pynput (mouse/keyboard controllers for input injection), time (stdlib, sleep/timing), threading (non-blocking playback loop)
- **Storage**: In-memory (reads from the current macro loaded via RecordingService or PersistenceService)
- **Testing**: TBD (pytest recommended)
- **Target Platform**: Windows (primary), macOS (best-effort)
- **Project Type**: Desktop app
- **Constraints**: Timing accuracy within 100ms; stop response under 500ms; support 999+ loop iterations

## Project Structure

```text
macro_app/
├── main.py
├── domain/
│   └── models.py               # PlaybackSession (added to existing)
├── application/
│   ├── recording_service.py    # (from recording plan)
│   └── playback_service.py    # PlaybackService
├── infrastructure/
│   ├── pynput_listener.py      # (from recording plan)
│   └── pynput_controller.py   # PynputController adapter
├── presentation/
│   └── api.py                  # JS API bridge (play_start, play_stop)
├── macros/
└── frontend/
```

**Structure Decision**: Extends the existing hexagonal structure. Adds `PlaybackService` to the application layer and `PynputController` to infrastructure for output injection (counterpart to the listener for input).

## Phase 1: Domain Model Extension

**Purpose**: Add the playback session model

- [ ] T023 Extend `domain/models.py` with `PlaybackSession` data class: `macro_events` (List[MacroEvent]), `loop_count` (int, 1 = no loop, special value like -1 = infinite), `current_loop` (int), `delay_between_loops` (int, ms), `is_playing` (bool), `current_event_index` (int)

---

## Phase 2: Infrastructure — Pynput Controller Adapter

**Purpose**: Wrap pynput's input injection behind a clean interface

- [ ] T024 Implement `PynputController` class in `infrastructure/pynput_controller.py`: wraps pynput `mouse.Controller` and `keyboard.Controller`
- [ ] T025 Implement `execute_event(event: MacroEvent)` method: dispatches based on `event_type` (mouse_click → controller.click/position, key_press → controller.press, key_release → controller.release, mouse_move → controller.position)
- [ ] T026 Implement `mouse_click(button, x, y)` internal: positions mouse then clicks the specified button
- [ ] T027 Implement `key_action(key, is_press)` internal: presses or releases the specified key

---

## Phase 3: Application — Playback Service

**Purpose**: Orchestrate the playback use case

- [ ] T028 Implement `PlaybackService` class in `application/playback_service.py`; depends on `PynputController` (injected via constructor)
- [ ] T029 Implement `set_macro(events: List[MacroEvent])`: stores the macro events to be played; rejects if called during active playback
- [ ] T030 Implement `play(loop_count: int = 1, delay_between_loops: int = 0)`: creates a PlaybackSession, spawns a daemon thread for the playback loop; emits "playback_started" signal
- [ ] T031 Implement the playback loop logic (private method `_run_playback`): iterates through events, sleeps for the delta between consecutive timestamps, calls `controller.execute_event()`, handles loop count and inter-loop delay
- [ ] T032 Implement `stop()`: sets `is_playing = False`, the playback thread detects this and exits cleanly; emits "playback_stopped" signal
- [ ] T033 Implement `is_playing` property for state checks
- [ ] T034 Add guard: reject `play()` if no macro is set or if already playing
- [ ] T035 Add guard: reject `set_macro()` if currently playing
- [ ] T036 Handle the "infinite loop" case: when `loop_count = -1`, the outer loop never terminates on its own

---

## Phase 4: Presentation — Pywebview API Bridge (Playback)

**Purpose**: Expose playback controls to the frontend JavaScript

- [ ] T037 Implement `play_macro(loop_count, delay)` API function in `presentation/api.py`: calls `PlaybackService.play()`
- [ ] T038 Implement `stop_playback()` API function in `presentation/api.py`: calls `PlaybackService.stop()`
- [ ] T039 Implement `get_playback_state()` API function: returns current playback status (is_playing, current_loop, progress)

---

## Phase 5: Integration

**Purpose**: Wire playback service into main.py

- [ ] T040 In `main.py`, instantiate `PynputController`, inject into `PlaybackService`, register new API functions with pywebview

---

## Dependencies & Execution Order

- **Phase 1 (Domain)**: Depends on macro-recording Phase 2 (needs `MacroEvent` from models.py)
- **Phase 2 (Infrastructure)**: Depends on Phase 1 (needs `MacroEvent`)
- **Phase 3 (Application)**: Depends on Phase 1 (models) and Phase 2 (controller)
- **Phase 4 (Presentation)**: Depends on Phase 3 (service)
- **Phase 5 (Integration)**: Depends on all previous phases
