# Feature Specification: Recording Panel (Frontend)

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Start and Stop Recording from the UI (Priority: P1)

The user opens the app, sees a "Record" button, clicks it to start recording their game actions, then clicks the same button (now labeled "Stop") to end the recording. The button shows clear visual feedback for both states.

**Why this priority**: This is the primary direct-UI interaction for the core recording feature. Even though hotkeys exist, the UI button is the fallback and initial interaction point.

**Independent Test**: Open the app, click Record, verify the button changes to "Stop" and the status updates. Click Stop, verify the button returns to "Record" and the event count appears.

**Acceptance Scenarios**:

1. **Scenario**: Start recording via button click
   - **Given** the app is idle (not recording, not playing)
   - **When** the user clicks the "Start Recording" button
   - **Then** the button text changes to "Stop Recording", the button color changes to red (active state), the status bar shows "Recording", and the Playback and Edit panels are disabled

2. **Scenario**: Stop recording via button click
   - **Given** the app is actively recording
   - **When** the user clicks the "Stop Recording" button
   - **Then** the button returns to "Start Recording" with default color, the status bar shows "Ready" with the event count, and the Playback and Edit panels re-enable

---

### Edge Cases

- What if the Record button is clicked while playback is active? (should be disabled — the API layer already handles the guard, but the UI should reflect it)
- What if recording is started via hotkey while the UI is open? (the button state should update to reflect the change — handled by state polling)
- What if the backend returns an error (e.g., `Already recording`)? (show a brief error message)

## Requirements

### Functional Requirements

- **FR-001**: The UI MUST display a toggle button labeled "Start Recording" when idle and "Stop Recording" when active.
- **FR-002**: The button MUST be visually distinct between states (color, icon, or text change).
- **FR-003**: The button MUST be disabled when a macro is being played back.
- **FR-004**: After stopping, the UI MUST display the number of events captured (e.g., "Captured 42 events").
- **FR-005**: The panel MUST poll `get_app_state()` every 500ms to stay synchronized with hotkey-triggered state changes.

### Key Entities

- **Recording state**: `is_recording` (boolean), sourced from `get_app_state()`.

## Success Criteria

- **SC-001**: Button state changes from click to visual update within 200ms.
- **SC-002**: Hotkey-triggered recording state is reflected in the UI within 1 second (via polling).
