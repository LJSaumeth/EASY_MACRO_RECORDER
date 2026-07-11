# Feature Specification: Macro Recording

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Start and Stop Recording (Priority: P1)

The user wants to record a sequence of mouse clicks and keyboard presses to automate in-game XP grinding. They start recording, perform the desired actions in their game, then stop recording. The macro is held in memory ready for playback or saving.

**Why this priority**: Recording is the foundation of the entire app. Without it, nothing else matters.

**Independent Test**: Start recording, click and type a few times, stop recording. Verify the app confirms recording started, events were captured, and recording stopped.

**Acceptance Scenarios**:

1. **Scenario**: User starts recording successfully
   - **Given** the app is running and no recording is active
   - **When** the user triggers "start recording"
   - **Then** the app enters recording state and begins capturing mouse clicks and keyboard presses with relative timestamps

2. **Scenario**: User stops recording successfully
   - **Given** the app is actively recording
   - **When** the user triggers "stop recording"
   - **Then** the app stops capturing input, stores the recorded events in memory, and exits recording state

3. **Scenario**: Recording captures input outside the app window
   - **Given** the app is recording and the user focuses on their game window
   - **When** the user clicks and types inside the game window
   - **Then** all mouse clicks and keyboard presses inside the game are captured

---

### User Story 2 - Event Timestamp Accuracy (Priority: P2)

The user needs recorded events to maintain accurate relative timing so that the macro replays exactly as performed — crucial for timing-sensitive game actions.

**Why this priority**: Without accurate timing, playback won't work correctly in real-game scenarios.

**Independent Test**: Record a sequence with intentional pauses, inspect the recorded timestamps. Verify each event's timestamp matches the actual time elapsed since recording started.

**Acceptance Scenarios**:

1. **Scenario**: Events record with correct relative timing
   - **Given** recording is active
   - **When** user clicks, waits 2 seconds, then presses a key, then clicks again
   - **Then** the recorded events show timestamps at approximately 0s (first click), 2s (key press), and 2.xs (second click) relative to recording start

---

### Edge Cases

- What happens when the user triggers "start recording" while already recording? (should be ignored or show a warning)
- What happens if no events are captured before stopping? (macro should be empty but valid)
- What happens if the game crashes or closes during recording? (recording should continue capturing whatever input is possible — OS-level events are still captured by pynput)
- How does the system handle very long recordings (thousands of events)? (should not crash or degrade)

## Requirements

### Functional Requirements

- **FR-001**: System MUST start capturing mouse clicks and keyboard presses when recording is triggered.
- **FR-002**: System MUST stop capturing input when recording is stopped.
- **FR-003**: System MUST timestamp each captured event relative to the moment recording started (in milliseconds).
- **FR-004**: System MUST capture input globally (outside the app's own window via pynput listeners).
- **FR-005**: System MUST store the recorded macro in memory as an ordered list of events with timestamps.
- **FR-006**: System MUST NOT capture input from the app's own UI controls (start/stop buttons) as part of the macro.
- **FR-007**: System MUST provide a way to signal recording state changes to the frontend (via pywebview JS API).

### Key Entities

- **Macro Event**: Represents a single recorded input action. Key attributes: `type` (mouse_click, mouse_move, key_press, key_release), `timestamp` (ms since recording start), action-specific data (button type, key name, coordinates).
- **Recording Session**: Represents an active recording. Holds a list of `MacroEvent` objects. Key attributes: `start_time`, `events[]`, `is_recording` (boolean).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Recording can be started and stopped within 1 second of trigger.
- **SC-002**: Event timestamps are accurate to within 50ms of actual input time.
- **SC-003**: System handles recordings of at least 10,000 events without performance degradation.
- **SC-004**: Recording works while the game window has focus (global input capture).
