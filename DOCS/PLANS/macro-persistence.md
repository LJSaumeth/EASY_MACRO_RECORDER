# Implementation Plan: Macro Persistence

**Date**: 2026-07-11
**Spec**: [macro-persistence.md](../SPECS/macro-persistence.md)

## Summary

Implement CRUD operations for macro files: save macros to .json files in the `macros/` directory, load macros from .json files, list all available macros, and delete macros. Includes automatic directory creation, JSON schema validation, filename sanitization, and graceful filesystem error handling.

## Clean Code Guidelines

All code written for this feature will follow Clean Code principles: meaningful names for variables, functions, and classes that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; consistent error handling with explicit return values or exceptions where appropriate; no magic numbers — all constants extracted to named variables; and the hexagonal architecture layers will be strictly respected so that domain logic never depends on infrastructure details.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: json (stdlib), os/pathlib (stdlib, filesystem ops)
- **Storage**: Filesystem — `macros/` directory containing .json files
- **Testing**: TBD (pytest recommended, with tmp_path fixture)
- **Target Platform**: Windows (primary), macOS (best-effort)
- **Project Type**: Desktop app
- **Constraints**: Save/load under 1s for 5k events; listing under 200ms; no partial writes

## Project Structure

```text
macro_app/
├── main.py
├── domain/
│   └── models.py               # Macro (serializable model)
├── application/
│   ├── recording_service.py    # (from recording plan)
│   ├── playback_service.py    # (from playback plan)
│   └── persistence_service.py # MacroRepository
├── infrastructure/
│   ├── pynput_listener.py
│   ├── pynput_controller.py
│   └── json_file_storage.py   # JsonFileStorage adapter
├── presentation/
│   └── api.py
├── macros/                     # Runtime .json storage directory
└── frontend/
```

**Structure Decision**: Adds `Macro` domain model (full serializable macro with metadata), `PersistenceService` in the application layer (use case orchestration), and `JsonFileStorage` in infrastructure (filesystem adapter). The `macros/` directory is created at startup.

## Phase 1: Domain Model Extension

**Purpose**: Serialization-friendly macro model

- [ ] T041 Extend `domain/models.py` with `Macro` data class: `name` (str), `events` (List[MacroEvent]), `created_at` (str, ISO format), `updated_at` (str, ISO format)
- [ ] T042 Implement `Macro.to_dict()` and `Macro.from_dict(data: dict)` methods for JSON serialization/deserialization

---

## Phase 2: Infrastructure — JSON File Storage Adapter

**Purpose**: Interface with the filesystem, isolated from application logic

- [ ] T043 Implement `JsonFileStorage` class in `infrastructure/json_file_storage.py`; receives `storage_path` (the `macros/` directory path) via constructor
- [ ] T044 Implement `ensure_directory()`: creates `storage_path` if it doesn't exist (called on init)
- [ ] T045 Implement `filename_for(name: str) -> Path`: sanitizes the name (only alphanumeric, hyphens, underscores; strip invalid chars) and returns the full `.json` path
- [ ] T046 Implement `save(macro: Macro)`: serializes `macro.to_dict()` using `json.dump()`, writes atomically (write to temp file, then rename to target path) to prevent partial writes
- [ ] T047 Implement `load(name: str) -> Macro`: reads the file, deserializes with `json.load()`, validates the structure (must have `events` key as a list), returns a `Macro` via `from_dict()`; raises custom `MacroNotFoundError` or `CorruptedMacroError` as appropriate
- [ ] T048 Implement `list_all() -> List[str]`: iterates all `.json` files in `storage_path`, returns list of basenames without extension
- [ ] T049 Implement `delete(name: str)`: removes the file; raises `MacroNotFoundError` if file doesn't exist
- [ ] T050 Define custom exceptions in a new `domain/exceptions.py`: `MacroNotFoundError`, `CorruptedMacroError`, `InvalidMacroNameError`

---

## Phase 3: Application — Persistence Service

**Purpose**: Orchestrate persistence use cases, thin wrapper over the storage adapter

- [ ] T051 Implement `PersistenceService` class in `application/persistence_service.py`; depends on `JsonFileStorage` (injected via constructor)
- [ ] T052 Implement `save_macro(name: str, events: List[MacroEvent]) -> Macro`: creates a `Macro` object, calls `storage.save()`; returns the saved `Macro`
- [ ] T053 Implement `load_macro(name: str) -> Macro`: calls `storage.load()`, returns the `Macro`; catches exceptions and propagates them with context
- [ ] T054 Implement `list_macros() -> List[str]`: calls `storage.list_all()`
- [ ] T055 Implement `delete_macro(name: str)`: calls `storage.delete()`
- [ ] T056 Implement name validation: reject empty names, names longer than 100 characters, names with only invalid characters after sanitization

---

## Phase 4: Presentation — Pywebview API Bridge (Persistence)

**Purpose**: Expose persistence operations to the frontend

- [ ] T057 Implement `save_macro(name)` API function: calls `PersistenceService.save_macro()` with current RecordingService events
- [ ] T058 Implement `load_macro(name)` API function: calls `PersistenceService.load_macro()`, stores result in PlaybackService
- [ ] T059 Implement `list_macros()` API function: calls `PersistenceService.list_macros()`, returns list to JS
- [ ] T060 Implement `delete_macro(name)` API function: calls `PersistenceService.delete_macro()`, returns success/error to JS

---

## Phase 5: Integration

**Purpose**: Wire persistence into main.py

- [ ] T061 In `main.py`, instantiate `JsonFileStorage` with the `macros/` path, inject into `PersistenceService`, register new API functions; ensure `macros/` is created on app startup

---

## Dependencies & Execution Order

- **Phase 1 (Domain)**: Depends on macro-recording Phase 2 (needs `MacroEvent` from models.py)
- **Phase 2 (Infrastructure)**: Depends on Phase 1 (needs `Macro`, exceptions)
- **Phase 3 (Application)**: Depends on Phase 1 (models) and Phase 2 (storage adapter); also depends on `RecordingService.get_current_macro()` from recording plan
- **Phase 4 (Presentation)**: Depends on Phase 3 (service)
- **Phase 5 (Integration)**: Depends on all previous phases
