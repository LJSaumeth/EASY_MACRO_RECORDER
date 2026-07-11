# Implementation Plan: Hotkey Configuration Panel (Frontend)

**Date**: 2026-07-11
**Spec**: [frontend-hotkey-config.md](../SPECS/frontend-hotkey-config.md)

## Summary

Implement hotkey configuration UI: a table showing action → key mappings with a Change button per row, a key capture overlay that listens for a single keypress, and a Reset to Defaults button. Error messages from the backend (conflicts, OS-reserved) are displayed inline.

## Clean Code Guidelines

All frontend code will follow Clean Code principles: meaningful variable and function names that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; CSS classes named by purpose, not by appearance; event handlers kept thin — they delegate to named service functions; DOM queries cached in variables at module scope where reused; and the JavaScript module pattern will be used to avoid global namespace pollution.

## Technical Context

- **Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Primary Dependencies**: None
- **Backend API**: `window.pywebview.api.get_hotkeys()`, `window.pywebview.api.set_hotkey(action, key)`, `window.pywebview.api.reset_hotkeys_to_default()`
- **Target Platform**: Rendered via pywebview (Chromium-based on Windows)
- **Note**: Key capture for rebinding uses a DOM `keydown` event listener on the capture overlay — NOT a backend listener. The frontend captures the key name, then sends it to the backend API.

## Project Structure

```text
macro_app/frontend/
├── index.html     # Hotkey section in #hotkey-panel, capture overlay div
├── style.css      # Styles prefixed with .hotkey-*
└── app.js         # HotkeyPanel namespace object
```

## Phase 1: HTML Structure

- [ ] T150 Add hotkey configuration section to `index.html`:
  - `<section id="hotkey-panel">`
  - Bindings table: `<table id="hotkey-table">` with columns: Action, Key, Change button
  - Reset to Defaults button
  - Error message display span
  - Key capture overlay: `<div id="key-capture-overlay" class="hidden">` with a prompt message and timeout indicator; captures `keydown` events

## Phase 2: CSS Styling

- [ ] T151 Style the hotkey panel: `.hotkey-panel` layout, `.hotkey-table` compact table, `.hotkey-change-btn` small button style, `.hotkey-error` red error text, `#key-capture-overlay` centered modal overlay with semi-transparent backdrop, `.capture-prompt` large centered text ("Press a key..."), `.capture-timeout` countdown indicator

## Phase 3: JavaScript Logic

- [ ] T152 Create `HotkeyPanel` module in `app.js` with cached DOM references
- [ ] T153 Implement `refreshBindingsTable()`: calls `api.get_hotkeys()`, builds table rows with action name (human-readable), current key, and Change button; clears error display
- [ ] T154 Implement `startKeyCapture(action)`: shows the capture overlay, starts a 5-second timeout countdown, attaches a one-time `keydown` listener to the document
- [ ] T155 Implement `onKeyCaptured(event)`: extracts key name from the event (handles special keys like F1-F12, Escape, etc.), calls `api.set_hotkey(action, key)`, hides overlay, refreshes table; if backend returns error, shows it in the error span
- [ ] T156 Implement `cancelCapture()`: hides overlay, removes listener, clears timeout (called on timeout or Escape key)
- [ ] T157 Implement `resetToDefaults()`: `confirm()` guard, calls `api.reset_hotkeys_to_default()`, refreshes table
- [ ] T158 Implement `normalizeKeyName(event)`: converts `event.key`/`event.code` into the pynput-compatible key name (e.g., "F6", "escape", "a")
- [ ] T159 Bind Change button events (delegated via table click), Reset button, and overlay dismiss

## Phase 4: Integration

- [ ] T160 Initial call to `refreshBindingsTable()` on app startup (inside `pywebviewready`)
- [ ] T161 No polling needed for this panel — hotkey config is static until user changes it
- [ ] T162 Reset button disabled during recording or playback to prevent mid-session rebinding

## Dependencies & Execution Order

- Phase 1 → 2 → 3 → 4
- No dependencies on other panels
- `updateState()` from polling is only needed to disable Reset during active recording/playback
