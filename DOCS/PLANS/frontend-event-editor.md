# Implementation Plan: Event Editor Panel (Frontend)

**Date**: 2026-07-11
**Spec**: [frontend-event-editor.md](../SPECS/frontend-event-editor.md)

## Summary

Implement the macro event viewer and editor: an HTML table showing all recorded/loaded events, per-row Delete and Adjust Timing controls, an Insert Event form, an Insert Delay form, and a Clear All button. All edit controls are disabled during recording or playback.

## Clean Code Guidelines

All frontend code will follow Clean Code principles: meaningful variable and function names that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; CSS classes named by purpose, not by appearance; event handlers kept thin — they delegate to named service functions; DOM queries cached in variables at module scope where reused; and the JavaScript module pattern will be used to avoid global namespace pollution.

## Technical Context

- **Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Primary Dependencies**: None
- **Backend API**: `window.pywebview.api.get_macro_events()`, `window.pywebview.api.delete_macro_event(index)`, `window.pywebview.api.adjust_event_timestamp(index, delta_ms)`, `window.pywebview.api.insert_macro_event(...)`, `window.pywebview.api.insert_macro_delay(index, duration)`, `window.pywebview.api.clear_macro_events()`, `window.pywebview.api.can_edit_macro()`, `window.pywebview.api.get_app_state()`
- **Target Platform**: Rendered via pywebview (Chromium-based on Windows)

## Project Structure

```text
macro_app/frontend/
├── index.html     # Editor section in #editor-panel
├── style.css      # Styles prefixed with .editor-*
└── app.js         # EditorPanel namespace object
```

## Phase 1: HTML Structure

- [ ] T135 Add event editor section to `index.html`: `<section id="editor-panel">`
  - Event table: `<table id="event-table">` with `<thead>` (Index, Type, Timestamp, Details, Delete, Adjust) and `<tbody>`
  - Empty state message: `<p id="editor-empty-msg">`
  - Delete button per row (generated dynamically in JS)
  - Adjust Timing: per-row number input + Apply button (generated dynamically)
  - Insert Event form: type dropdown, position index input, x/y fields (shown for mouse), key field (shown for keyboard), Add button
  - Insert Delay form: position index input, duration input, Add button
  - Clear All button

## Phase 2: CSS Styling

- [ ] T136 Style the editor panel: `.editor-panel` layout, `.event-table` compact table styling (monospace font for details), `.editor-empty` centered placeholder, `.editor-btn-danger` for Delete/Clear buttons (red), `.editor-form-row` for insert forms, `.editor-disabled` grayed-out state

## Phase 3: JavaScript Logic

- [ ] T137 Create `EditorPanel` module in `app.js` with cached DOM references
- [ ] T138 Implement `refreshEventTable()`: calls `api.get_macro_events()`, clears tbody, builds rows dynamically with data attributes for event index; shows/hides empty state message; called after recording stops, after load, and after every edit
- [ ] T139 Implement `deleteEvent(index)`: calls `api.delete_macro_event(index)`, refreshes table on success
- [ ] T140 Implement `adjustTimestamp(index, deltaMs)`: reads the per-row delta input value, calls `api.adjust_event_timestamp(index, delta)`, refreshes table on success
- [ ] T141 Implement `insertEvent()`: reads form values (type, index, coordinates/key), calls `api.insert_macro_event(...)`, refreshes table, clears form
- [ ] T142 Implement `insertDelay()`: reads form values (index, duration), calls `api.insert_macro_delay(...)`, refreshes table, clears form
- [ ] T143 Implement `clearAll()`: `confirm()` guard, calls `api.clear_macro_events()`, refreshes table
- [ ] T144 Implement `updateState(state)`: enables/disables all edit controls based on `can_edit`; toggles the `.editor-disabled` class on the panel
- [ ] T145 Implement form field visibility toggle: when Insert Event type changes to "mouse_click"/"mouse_move", show x/y fields; when "key_press"/"key_release", show key field; when "mouse_click", also show button dropdown
- [ ] T146 Implement `formatEventDetails(event)`: returns a human-readable string like `left @ (500,300)` or `key 'a'` depending on event type

## Phase 4: Integration

- [ ] T147 Wire `EditorPanel.updateState()` into the global state polling loop
- [ ] T148 Expose `refreshEventTable()` globally so `FilePanel` can call it after loading a macro
- [ ] T149 Auto-refresh table when recording stops (detected via state change in polling loop: `is_recording` transitions from true to false)

## Dependencies & Execution Order

- Phase 1 → 2 → 3 → 4
- Exposes `refreshEventTable()` for File Panel integration
- Relies on global state polling loop
