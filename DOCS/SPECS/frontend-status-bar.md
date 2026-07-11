# Feature Specification: Global Status Bar (Frontend)

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - See App State at a Glance (Priority: P1)

The user always sees a status bar at the bottom of the window showing whether the app is idle ("Ready"), recording, or playing back — along with relevant progress info.

**Why this priority**: The status bar is the single source of truth for the app's current state. Every other component depends on it for clarity.

**Independent Test**: Record a macro. Verify the status bar shows "Recording..." with a blinking indicator. Stop recording. Verify it shows "Ready" + event count.

**Acceptance Scenarios**:

1. **Scenario**: Idle state
   - **Given** the app is open with no active recording or playback
   - **When** the user looks at the status bar
   - **Then** it displays "Ready" with the loaded event count (or "No macro loaded" if empty)

2. **Scenario**: Recording state
   - **Given** recording is active
   - **When** the user looks at the status bar
   - **Then** it displays a red indicator with "Recording..." and the live event count

3. **Scenario**: Playback state
   - **Given** playback is active with loop 2 of 5
   - **When** the user looks at the status bar
   - **Then** it displays a green indicator with "Playing (Loop 2/5)" and the current event index

4. **Scenario**: Error state
   - **Given** a backend operation returned an error
   - **When** the error is received
   - **Then** the status bar briefly shows the error message in a warning color for 3 seconds, then returns to the normal state

---

### Edge Cases

- What if both recording and playback are somehow active? (should never happen due to backend guards, but display "Recording" as priority)
- What if the status bar text is too long? (truncate with ellipsis)
- What if polling fails (backend unreachable)? (show "Connection lost" in warning color)

## Requirements

### Functional Requirements

- **FR-001**: The status bar MUST be always visible at the bottom of the window.
- **FR-002**: The status bar MUST display the current app state: "Ready", "Recording...", or "Playing".
- **FR-003**: The status bar MUST show the loaded event count when idle (e.g., "Ready — 42 events loaded").
- **FR-004**: The status bar MUST show loop progress during playback (e.g., "Loop 2/5").
- **FR-005**: The status bar MUST use color-coded indicators: gray for idle, red for recording, green for playback, orange/yellow for errors.
- **FR-006**: Temporary messages (errors, confirmations) MUST auto-dismiss after 3 seconds and revert to the normal state.

### Key Entities

- **App state**: `is_recording` (bool), `is_playing` (bool), `playback.current_loop` (int), `playback.loop_count` (int), event count (int), `can_edit` (bool).

## Success Criteria

- **SC-001**: Status bar updates within 200ms of any state change.
- **SC-002**: Status bar text is always readable against the bar background.
- **SC-003**: Temporary messages do not overlap or stack (latest replaces previous).
