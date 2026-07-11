# Implementation Plan: File Management Panel (Frontend)

**Date**: 2026-07-11
**Spec**: [frontend-file-management.md](../SPECS/frontend-file-management.md)

## Summary

Implement macro file operations UI: text input + Save button for saving recorded macros, a dropdown + Load/Delete buttons for managing saved macros. The dropdown refreshes after every save/delete. Delete requires confirmation. Event count updates after load.

## Clean Code Guidelines

All frontend code will follow Clean Code principles: meaningful variable and function names that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; CSS classes named by purpose, not by appearance; event handlers kept thin — they delegate to named service functions; DOM queries cached in variables at module scope where reused; and the JavaScript module pattern will be used to avoid global namespace pollution.

## Technical Context

- **Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Primary Dependencies**: None
- **Backend API**: `window.pywebview.api.save_macro(name)`, `window.pywebview.api.load_macro(name)`, `window.pywebview.api.list_macros()`, `window.pywebview.api.delete_macro(name)`, `window.pywebview.api.get_app_state()`
- **Target Platform**: Rendered via pywebview (Chromium-based on Windows)

## Project Structure

```text
macro_app/frontend/
├── index.html     # File management section in #file-panel
├── style.css      # Styles prefixed with .file-*
└── app.js         # FilePanel namespace object
```

## Phase 1: HTML Structure

- [ ] T123 Add file management section to `index.html`: `<section id="file-panel">` containing name text input, Save button, macro dropdown `<select>`, Load and Delete buttons, and a loaded-macro-info span

## Phase 2: CSS Styling

- [ ] T124 Style the file panel: `.file-panel` flexbox layout, `.file-save-row` for name input + button, `.file-list-row` for dropdown + Load + Delete, `.file-info` for loaded macro name and event count

## Phase 3: JavaScript Logic

- [ ] T125 Create `FilePanel` module in `app.js` with cached DOM references
- [ ] T126 Implement `refreshMacroList()`: calls `api.list_macros()`, populates `<select>` dropdown, adds placeholder `<option>` when empty ("No macros saved yet")
- [ ] T127 Implement `saveMacro()`: reads name input value, validates non-empty, calls `api.save_macro(name)`, shows result message, calls `refreshMacroList()`
- [ ] T128 Implement `loadMacro()`: reads selected value from dropdown, validates selection, calls `api.load_macro(name)`, updates loaded-macro info display, calls global event table refresh
- [ ] T129 Implement `deleteMacro()`: reads selected value, shows `confirm("Delete macro?")`, calls `api.delete_macro(name)` on confirm, calls `refreshMacroList()`, clears loaded macro if the deleted one was loaded
- [ ] T130 Implement `updateState(state)`: enables/disables Save button based on `is_recording` (Save only enabled when recording just stopped and events exist)
- [ ] T131 Bind Save/Load/Delete click events

## Phase 4: Integration

- [ ] T132 Wire `FilePanel.updateState()` into the global state polling loop
- [ ] T133 After load, trigger the Event Editor panel to refresh its table (via a pub/sub event or direct function call)
- [ ] T134 Initial call to `refreshMacroList()` on app startup

## Dependencies & Execution Order

- Phase 1 → 2 → 3 → 4
- Has a soft dependency on Event Editor (calls its refresh after load)
- Relies on global state polling loop
