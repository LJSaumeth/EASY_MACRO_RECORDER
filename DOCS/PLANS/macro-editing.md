# Implementation Plan: Macro Editing

**Date**: 2026-07-11
**Spec**: [macro-editing.md](../SPECS/macro-editing.md)

## Summary

Implement the ability to view, delete, and adjust events in a recorded macro, as well as insert new events manually. Operations include: returning the full event list for display, deleting events by index, shifting timestamps of individual events (with cascade adjustment of subsequent events), and inserting new click/key/delay events at any position. Editing is disabled during active recording or playback.

## Clean Code Guidelines

All code written for this feature will follow Clean Code principles: meaningful names for variables, functions, and classes that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; consistent error handling with explicit return values or exceptions where appropriate; no magic numbers — all constants extracted to named variables; and the hexagonal architecture layers will be strictly respected so that domain logic never depends on infrastructure details.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: None beyond stdlib (pure domain logic, no external libraries needed)
- **Storage**: Operates on the in-memory macro held by `RecordingService` or loaded via `PersistenceService`
- **Testing**: TBD (pytest recommended)
- **Target Platform**: Windows (primary), macOS (best-effort)
- **Project Type**: Desktop app
- **Constraints**: 1,000 event list returned in under 500ms; single event operations under 100ms

## Project Structure

```text
macro_app/
├── main.py
├── domain/
│   ├── models.py               # (existing)
│   └── exceptions.py           # (from persistence plan)
├── application/
│   ├── recording_service.py
│   ├── playback_service.py
│   ├── persistence_service.py
│   ├── hotkey_service.py
│   └── macro_editor.py        # MacroEditor
├── infrastructure/
│   └── ...                     # (no new infrastructure for this feature)
├── presentation/
│   └── api.py
├── macros/
└── frontend/
```

**Structure Decision**: Macro editing is a pure application-layer concern — no new infrastructure adapters needed. It operates on `List[MacroEvent]` in memory. `MacroEditor` is a service that takes a macro event list and performs mutation operations on it.

## Phase 1: Application — Macro Editor

**Purpose**: All editing logic — operates on the event list in memory

- [ ] T087 Implement `MacroEditor` class in `application/macro_editor.py`; depends on `RecordingService` and `PlaybackService` (injected — to check state and access/set the current macro events)
- [ ] T088 Implement `can_edit() -> bool`: returns `True` only when neither recording nor playback is active
- [ ] T089 Implement `get_events() -> List[MacroEvent]`: returns the full event list; if no macro is loaded, returns empty list; raises error if recording/playback is active
- [ ] T090 Implement `delete_event(index: int)`: validates `index` is within bounds, removes the event at that index from the list; raises `IndexError` if out of bounds
- [ ] T091 Implement `adjust_timestamp(index: int, delta_ms: int)`: adds `delta_ms` to the event at `index`; if the resulting timestamp < 0, clamp to 0; then cascade-adjust all subsequent events by the same delta to preserve relative spacing
- [ ] T092 Implement `insert_event(index: int, event: MacroEvent)`: inserts a new event at `index`; if `index >= len(events)`, appends; after insertion, adjusts timestamps of subsequent events to maintain ordering (shift later events forward by a small default gap if needed)
- [ ] T093 Implement `insert_delay(index: int, duration_ms: int)`: convenience method that inserts a delay by shifting all events from `index` onward by `duration_ms`
- [ ] T094 Implement `clear_all_events()`: removes all events from the current macro
- [ ] T095 Add guard to every mutation method: raise a custom `EditingNotAllowedError` if `can_edit()` is `False`

---

## Phase 2: Presentation — Pywebview API Bridge (Editing)

**Purpose**: Expose editing operations to the frontend

- [ ] T096 Implement `get_macro_events()` API function (extends the one from recording plan): returns full event list with index, type, timestamp, and details
- [ ] T097 Implement `delete_macro_event(index)` API function: calls `MacroEditor.delete_event()`
- [ ] T098 Implement `adjust_event_timestamp(index, delta_ms)` API function: calls `MacroEditor.adjust_timestamp()`
- [ ] T099 Implement `insert_macro_event(index, event_data)` API function: calls `MacroEditor.insert_event()`
- [ ] T100 Implement `insert_macro_delay(index, duration_ms)` API function: calls `MacroEditor.insert_delay()`
- [ ] T101 Implement `clear_macro_events()` API function: calls `MacroEditor.clear_all_events()`
- [ ] T102 Implement `can_edit_macro()` API function: calls `MacroEditor.can_edit()`, returns boolean to JS for UI state management (enable/disable edit controls)

---

## Phase 3: Integration

**Purpose**: Wire editor into main.py

- [ ] T103 In `main.py`, instantiate `MacroEditor` (inject `RecordingService` and `PlaybackService`), register all editing API functions with pywebview

---

## Dependencies & Execution Order

- **Phase 1 (Application)**: Depends on domain models (MacroEvent), RecordingService (recording plan), and PlaybackService (playback plan)
- **Phase 2 (Presentation)**: Depends on Phase 1
- **Phase 3 (Integration)**: Depends on all previous phases

This plan has no new infrastructure or domain model changes — it's pure application and presentation logic.
