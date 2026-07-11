# Implementation Plan: Hotkey System

**Date**: 2026-07-11
**Spec**: [hotkey-system.md](../SPECS/hotkey-system.md)

## Summary

Implement a global hotkey system using pynput's keyboard listener that allows users to control recording and playback without focusing the macro app window. Supports three actions: toggle recording (default F6), toggle playback (default F7), and emergency stop (default F8). Hotkeys are configurable and persisted across app restarts. Includes conflict detection to prevent duplicate assignments and OS-reserved key blocking.

## Clean Code Guidelines

All code written for this feature will follow Clean Code principles: meaningful names for variables, functions, and classes that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; consistent error handling with explicit return values or exceptions where appropriate; no magic numbers — all constants extracted to named variables; and the hexagonal architecture layers will be strictly respected so that domain logic never depends on infrastructure details.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: pynput (global keyboard listener for hotkey detection), json (stdlib, for hotkey config persistence)
- **Storage**: Hotkey configuration persisted as JSON (`macros/.hotkey_config.json` or in a settings file)
- **Testing**: TBD (pytest recommended)
- **Target Platform**: Windows (primary), macOS (best-effort)
- **Project Type**: Desktop app
- **Constraints**: Hotkey response under 200ms; works with any app in focus; zero missed presses

## Project Structure

```text
macro_app/
├── main.py
├── domain/
│   ├── models.py               # HotkeyBinding (added)
│   └── exceptions.py           # (from persistence plan)
├── application/
│   ├── recording_service.py
│   ├── playback_service.py
│   ├── persistence_service.py
│   └── hotkey_service.py      # HotkeyService
├── infrastructure/
│   ├── pynput_listener.py      # Extended with hotkey detection
│   ├── pynput_controller.py
│   ├── json_file_storage.py
│   └── hotkey_config_store.py  # HotkeyConfigStore
├── presentation/
│   └── api.py
├── macros/
└── frontend/
```

**Structure Decision**: The hotkey system reuses the existing pynput keyboard listener from the recording feature. A separate global listener thread runs continuously to detect hotkey presses. `HotkeyService` bridges between hotkey detection and the recording/playback services through a callback-based event system. Persistent config uses the existing JSON storage pattern.

## Phase 1: Domain Model Extension

**Purpose**: Hotkey data model

- [ ] T062 Add `HotkeyBinding` data class to `domain/models.py`: `action` (Literal["record_toggle", "playback_toggle", "emergency_stop"]), `key` (str, pynput key name), `modifiers` (List[str], optional)
- [ ] T063 Add `HotkeyConfig` data class to `domain/models.py`: `bindings` (List[HotkeyBinding])
- [ ] T064 Define default hotkey configuration: record_toggle=F6, playback_toggle=F7, emergency_stop=F8 (with no modifiers)
- [ ] T065 Add `HotkeyConfig.to_dict()` and `from_dict()` methods

---

## Phase 2: Infrastructure — Hotkey Config Store

**Purpose**: Persist hotkey configuration to disk

- [ ] T066 Implement `HotkeyConfigStore` class in `infrastructure/hotkey_config_store.py`; depends on `JsonFileStorage` (reuse existing) for read/write
- [ ] T067 Implement `load_config() -> HotkeyConfig`: reads config file, returns parsed config; if file missing, returns defaults
- [ ] T068 Implement `save_config(config: HotkeyConfig)`: writes config to disk

---

## Phase 3: Infrastructure — Global Hotkey Listener

**Purpose**: Detect hotkey presses globally (separate from recording listener)

- [ ] T069 Extend `PynputListener` or create a `GlobalHotkeyListener` in `infrastructure/pynput_listener.py`: a dedicated keyboard listener that runs for the entire app lifetime
- [ ] T070 Implement `register_hotkey(key, callback)`: maps a key combination to a callback function
- [ ] T071 Implement `unregister_hotkey(key)`: removes a hotkey binding
- [ ] T072 Implement `clear_all_hotkeys()`: removes all bindings
- [ ] T073 The listener checks each keypress against registered hotkeys and fires the callback on match; non-hotkey keys are ignored

---

## Phase 4: Application — Hotkey Service

**Purpose**: Manage hotkey bindings and route them to the correct service

- [ ] T074 Implement `HotkeyService` class in `application/hotkey_service.py`; depends on `GlobalHotkeyListener`, `HotkeyConfigStore`, `RecordingService`, `PlaybackService` (all injected)
- [ ] T075 Implement `initialize()`: loads config from store, registers all bindings with the listener, sets up callbacks that call the appropriate service methods
- [ ] T076 Implement `set_hotkey(action: str, key: str, modifiers: List[str] = None)`: validates no duplicate assignment and no OS-reserved key, updates the binding, re-registers with listener, saves config
- [ ] T077 Implement `get_bindings() -> List[HotkeyBinding]`: returns current bindings
- [ ] T078 Implement conflict detection: `_check_conflict(key, modifiers, exclude_action)` — checks if the key combo is already assigned to another action
- [ ] T079 Implement OS-reserved key filter: a deny-list of known reserved combinations (e.g., Alt+F4, Ctrl+Alt+Del, Win+L)
- [ ] T080 Implement `shutdown()`: clears all hotkeys, stops the listener

---

## Phase 5: Presentation — Pywebview API Bridge (Hotkeys)

**Purpose**: Expose hotkey configuration to the frontend

- [ ] T081 Implement `get_hotkeys()` API function: returns current hotkey bindings
- [ ] T082 Implement `set_hotkey(action, key, modifiers)` API function: updates a hotkey binding
- [ ] T083 Implement `reset_hotkeys_to_default()` API function: restores default bindings

---

## Phase 6: Integration

**Purpose**: Wire hotkey system into main.py

- [ ] T084 In `main.py`, instantiate `HotkeyConfigStore`, `HotkeyService` (injecting listener, store, recording service, playback service), call `hotkey_service.initialize()` on startup and `hotkey_service.shutdown()` on exit
- [ ] T085 Ensure the global hotkey listener starts on app launch and runs for the app's entire lifetime
- [ ] T086 Register hotkey API functions with pywebview

---

## Dependencies & Execution Order

- **Phase 1 (Domain)**: No dependencies (can run in parallel with other domain work)
- **Phase 2 (Infrastructure — Config Store)**: Depends on Phase 1 and persistence plan Phase 2 (JsonFileStorage)
- **Phase 3 (Infrastructure — Listener)**: Depends on Phase 1
- **Phase 4 (Application)**: Depends on Phases 1-3, recording plan Phase 4 (RecordingService), and playback plan Phase 3 (PlaybackService)
- **Phase 5 (Presentation)**: Depends on Phase 4
- **Phase 6 (Integration)**: Depends on all previous phases of this plan and the recording/playback/persistence plans
