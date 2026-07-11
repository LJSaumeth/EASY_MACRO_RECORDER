# Implementation Plan: Playback Panel (Frontend)

**Date**: 2026-07-11
**Spec**: [frontend-playback-panel.md](../SPECS/frontend-playback-panel.md)

## Summary

Implement a playback control section: Play/Stop toggle button, loop count input with infinite checkbox, and delay-between-loops input. All inputs validate on blur. The panel disables during recording and when no macro is loaded.

## Clean Code Guidelines

All frontend code will follow Clean Code principles: meaningful variable and function names that reveal intent; small, single-responsibility functions (no function longer than ~20 lines); no comments explaining what the code does — the code must be self-documenting; CSS classes named by purpose, not by appearance; event handlers kept thin — they delegate to named service functions; DOM queries cached in variables at module scope where reused; and the JavaScript module pattern will be used to avoid global namespace pollution.

## Technical Context

- **Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Primary Dependencies**: None
- **Backend API**: `window.pywebview.api.play_macro(loop_count, delay)`, `window.pywebview.api.stop_playback()`, `window.pywebview.api.get_app_state()`
- **Target Platform**: Rendered via pywebview (Chromium-based on Windows)

## Project Structure

```text
macro_app/frontend/
├── index.html     # Playback section added inside #playback-panel
├── style.css      # Styles prefixed with .playback-*
└── app.js         # PlaybackPanel namespace object
```

## Phase 1: HTML Structure

- [ ] T112 Add playback panel section to `index.html`: `<section id="playback-panel">` containing Play/Stop button, loop count number input (min=1, max=999), infinite loop checkbox, delay input (min=0), and loop progress display span

## Phase 2: CSS Styling

- [ ] T113 Style the playback panel: `.playback-panel` layout using flexbox, `.playback-btn` base and active states, `.playback-config` row layout for inputs, `.playback-progress` text style

## Phase 3: JavaScript Logic

- [ ] T114 Create `PlaybackPanel` module in `app.js` with cached DOM references
- [ ] T115 Implement `togglePlayback()`: reads loop count (or -1 if infinite), delay value; calls `api.play_macro()` or `api.stop_playback()` accordingly
- [ ] T116 Implement `validateInputs()`: clamps loop count to 1-999, delay to min 0, called on blur events
- [ ] T117 Implement `onInfiniteToggle()`: when checked, disables loop count input and sets its display to "infinity"; when unchecked, re-enables it
- [ ] T118 Implement `updateState(state)`: updates button text/class, enables/disables based on `is_recording` and `is_playing`; updates loop progress display from `state.playback`
- [ ] T119 Bind button click, input blur, checkbox change events

## Phase 4: Integration

- [ ] T120 Wire `PlaybackPanel.updateState()` into the global state polling loop
- [ ] T121 Play button disabled when `is_recording` or when macro has 0 events
- [ ] T122 Infinite checkbox state persisted in the panel module (not in backend — it's a UI convenience toggle)

## Dependencies & Execution Order

- Phase 1 → 2 → 3 → 4
- No dependencies on other panels
- Relies on global state polling loop
