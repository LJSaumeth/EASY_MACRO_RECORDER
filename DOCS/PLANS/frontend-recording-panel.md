# Implementation Plan: Recording Panel (Frontend)

**Date**: 2026-07-11
**Spec**: [frontend-recording-panel.md](../SPECS/frontend-recording-panel.md)

## Summary

Implement a recording control section in the UI: a toggle button that starts/stops recording, a visual state indicator, and an event count display after stopping. The button state syncs with the backend via polling `get_app_state()`.

## Clean Code Guidelines

All frontend code will follow Clean Code principles: meaningful variable and function names that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; CSS classes named by purpose, not by appearance; event handlers kept thin — they delegate to named service functions; DOM queries cached in variables at module scope where reused; and the JavaScript module pattern will be used to avoid global namespace pollution.

## Technical Context

- **Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Primary Dependencies**: None (no frameworks)
- **Backend API**: `window.pywebview.api.start_recording()`, `window.pywebview.api.stop_recording()`, `window.pywebview.api.get_app_state()`
- **Target Platform**: Rendered via pywebview (Chromium-based on Windows)
- **Project Type**: Single-page desktop app frontend

## Project Structure

```text
macro_app/frontend/
├── index.html     # All HTML markup (shared across all panels)
├── style.css      # All styles (shared across all panels)
└── app.js         # All JavaScript logic (shared across all panels)
```

**Structure Decision**: Single-file-per-layer approach. No build step, no bundler. The recording panel adds HTML elements to a `#recording-panel` section, CSS classes prefixed with `rec-`, and JS functions grouped under a `RecordingPanel` namespace object in `app.js`.

## Phase 1: HTML Structure

- [ ] T104 Add recording panel section to `index.html`: a `<section id="recording-panel">` containing a `<button id="rec-toggle-btn">` and a `<span id="rec-event-count">`

## Phase 2: CSS Styling

- [ ] T105 Style the recording panel in `style.css`: `.recording-panel` layout, `.rec-btn` base style (blue/gray), `.rec-btn.recording` active style (red, pulsing), `.rec-event-count` text style

## Phase 3: JavaScript Logic

- [ ] T106 Create `RecordingPanel` module in `app.js` with cached DOM references (`toggleBtn`, `eventCountSpan`)
- [ ] T107 Implement `toggleRecording()`: calls `api.start_recording()` or `api.stop_recording()` based on current state, updates button class and text on success
- [ ] T108 Implement `updateState(state)`: receives the full app state from the polling loop, updates button text/class/disabled-state and event count display
- [ ] T109 Bind button click event to `toggleRecording()` on DOMContentLoaded (via the main `pywebviewready` event)

## Phase 4: Integration

- [ ] T110 Wire `RecordingPanel.updateState()` into the global state polling loop (shared across all panels — defined in `app.js` main controller)
- [ ] T111 Ensure the record button is disabled when `state.is_playing` is true

## Dependencies & Execution Order

- Phase 1 → 2 → 3 → 4 (sequential within this plan)
- No dependencies on other frontend panel plans (they share files but logic is independent)
- Relies on the global state polling loop being established first (see Status Bar plan, which defines the main loop)
