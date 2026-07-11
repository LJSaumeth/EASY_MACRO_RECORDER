# Implementation Plan: Global Status Bar (Frontend)

**Date**: 2026-07-11
**Spec**: [frontend-status-bar.md](../SPECS/frontend-status-bar.md)

## Summary

Implement a persistent status bar at the bottom of the window showing the app's current state: idle ("Ready"), recording, or playing back. Includes color-coded indicators, event count, loop progress, and auto-dismissing temporary messages. Also implements the global state polling loop that drives all other panels.

## Clean Code Guidelines

All frontend code will follow Clean Code principles: meaningful variable and function names that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; CSS classes named by purpose, not by appearance; event handlers kept thin — they delegate to named service functions; DOM queries cached in variables at module scope where reused; and the JavaScript module pattern will be used to avoid global namespace pollution.

## Technical Context

- **Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Primary Dependencies**: None
- **Backend API**: `window.pywebview.api.get_app_state()` (polled every 500ms)
- **Target Platform**: Rendered via pywebview (Chromium-based on Windows)

## Project Structure

```text
macro_app/frontend/
├── index.html     # Status bar at the bottom of body
├── style.css      # Styles for .status-bar
└── app.js         # StatusBar module + main polling controller
```

## Phase 1: HTML Structure

- [ ] T163 Add status bar to `index.html`: `<footer id="status-bar">` containing a state indicator `<span>`, main status text `<span>`, and a temporary message `<span>`

## Phase 2: CSS Styling

- [ ] T164 Style the status bar: `.status-bar` fixed bottom, full width, flexbox layout, dark background, light text; `.status-indicator` small colored circle (gray/green/red/orange); `.status-text` main text; `.status-temp` temporary message styling (fades in/out)

## Phase 3: JavaScript Logic

- [ ] T165 Create `StatusBar` module in `app.js` with cached DOM references
- [ ] T166 Implement `setState(state)`: updates indicator color and text based on `is_recording` and `is_playing`; builds status text string (event count, loop progress)
- [ ] T167 Implement `showTempMessage(message, type)`: shows a temporary message (success/error/warning), auto-hides after 3 seconds using `setTimeout`, uses CSS transition for fade out
- [ ] T168 Implement `getStateColor(isRecording, isPlaying)`: returns "red" if recording, "green" if playing, "gray" if idle
- [ ] T169 Implement `getStateText(state)`: returns "Recording..." with live event count, "Playing (Loop X/Y)" with progress, or "Ready" with loaded event count

---

## Phase 4: Main Controller — State Polling Loop

**Purpose**: This is the central heartbeat that drives all panels. It must be defined first since every other panel depends on it.

- [ ] T170 Implement `AppController` module in `app.js`:
  - `startPolling()`: calls `api.get_app_state()` every 500ms via `setInterval`
  - `onStateReceived(state)`: calls `StatusBar.setState(state)`, then dispatches to each panel's `updateState(state)` method
  - `handleStateEvents(state)`: processes `state.events` array (recording_started, recording_stopped, playback_completed, etc.), calls `StatusBar.showTempMessage()` for relevant events, and triggers `EditorPanel.refreshEventTable()` on recording_stopped
  - Tracks previous state to detect transitions (e.g., `is_recording` changed from false to true)
- [ ] T171 Implement `init()`: waits for `pywebviewready` event, initializes all panels, starts polling
- [ ] T172 Export a `showMessage(message, type)` global helper that other panels can call to show status messages (wraps `StatusBar.showTempMessage`)

---

## Phase 5: Integration

- [ ] T173 Wire all panel `updateState()` calls in `AppController.onStateReceived()`
- [ ] T174 Ensure the polling loop starts on `pywebviewready` and the status bar is the first visible element

## Dependencies & Execution Order

- Phase 1 → 2 → 3 → 4 → 5
- This plan MUST be implemented first among all frontend plans because:
  1. The status bar is the first visible element on screen
  2. The polling loop in Phase 4 is a dependency for ALL other panels
  3. The `showMessage()` helper is used by every panel
- Other panels implement their `updateState(state)` method and register it with the controller
