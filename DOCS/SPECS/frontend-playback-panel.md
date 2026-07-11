# Feature Specification: Playback Panel (Frontend)

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Play and Stop Playback (Priority: P1)

The user has a macro loaded (recorded or imported). They click Play to start the macro replaying, and can click Stop to halt it mid-execution.

**Why this priority**: Direct UI control for the second core feature — playback — paired with recording.

**Independent Test**: Load a macro, click Play, verify the status changes to "Playing". Click Stop, verify it returns to "Ready".

**Acceptance Scenarios**:

1. **Scenario**: Play a loaded macro
   - **Given** a macro is loaded (events > 0) and the app is idle
   - **When** the user clicks "Play"
   - **Then** the button changes to "Stop", the status bar shows "Playing", the Recording panel and Editor panel are disabled

2. **Scenario**: Stop active playback
   - **Given** a macro is being replayed
   - **When** the user clicks "Stop"
   - **Then** playback stops, the button returns to "Play", the status returns to "Ready", and all panels re-enable

3. **Scenario**: Play button is disabled when no macro is loaded
   - **Given** no macro is loaded (0 events)
   - **When** the user views the Playback panel
   - **Then** the "Play" button is disabled or shows a message "No macro loaded"

---

### User Story 2 - Configure Loop Count and Delay (Priority: P2)

The user wants to set how many times the macro repeats and how long to pause between loops before starting playback.

**Why this priority**: Looping is the main differentiator for grinding use cases. UI controls make it configurable without re-recording.

**Independent Test**: Set loop count to 3, delay to 500ms, click Play. Verify the status bar shows "Loop 1/3", then "Loop 2/3", then "Loop 3/3", and playback completes.

**Acceptance Scenarios**:

1. **Scenario**: Set a fixed loop count
   - **Given** the Playback panel is active
   - **When** the user enters "5" in the loop count input
   - **Then** the value is stored and used when Play is clicked

2. **Scenario**: Toggle infinite loop
   - **Given** the Playback panel is active
   - **When** the user checks the "Repeat infinitely" checkbox
   - **Then** the loop count input is disabled and playback will repeat until manually stopped

3. **Scenario**: Set delay between loops
   - **Given** the Playback panel is active
   - **When** the user enters "2000" in the delay input field
   - **Then** a 2-second pause occurs between each loop iteration during playback

---

### Edge Cases

- What if the user enters a negative loop count? (clamp to 1, or show validation error)
- What if the delay is set to 0? (no delay — legal value, loop restarts immediately)
- What if Play is clicked while recording is active? (button should be disabled)
- What if playback completes naturally? (Play button should return to normal state)

## Requirements

### Functional Requirements

- **FR-001**: The panel MUST display a Play/Stop toggle button that reflects playback state.
- **FR-002**: The Play button MUST be disabled when no macro is loaded or when recording is active.
- **FR-003**: The panel MUST include a loop count input (integer, min 1, max 999) with default value 1.
- **FR-004**: The panel MUST include an "Infinite loop" checkbox that disables the loop count input.
- **FR-005**: The panel MUST include a "Delay between loops" input (ms, min 0) with default value 0.
- **FR-006**: The panel MUST poll `get_app_state()` to sync with hotkey-triggered playback changes.

### Key Entities

- **Playback configuration**: `loop_count` (int), `infinite_loop` (bool), `delay_between_loops` (int ms).

## Success Criteria

- **SC-001**: All inputs validate on blur (negative values rejected, loop count clamped to range).
- **SC-002**: Infinite loop checkbox immediately disables/enables the loop count field.
- **SC-003**: Playback progress (current loop / total loops) is visible during active playback.
