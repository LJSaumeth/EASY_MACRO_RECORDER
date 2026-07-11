# Feature Specification: Macro Playback

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Play Back a Recorded Macro Once (Priority: P1)

The user has recorded a macro and wants to replay it exactly as performed — same clicks, same keys, same timing — to automate one round of XP grinding.

**Why this priority**: Playback is the core value proposition. Users record to replay.

**Independent Test**: Record a short macro (e.g., click at coordinate + type a key), then play it back once. Verify the same actions are reproduced with the same timing.

**Acceptance Scenarios**:

1. **Scenario**: Playback reproduces all events in order
   - **Given** a macro with 3 events is stored in memory (click at 0ms, keypress at 1000ms, click at 2000ms)
   - **When** the user triggers playback
   - **Then** the system executes event 1 immediately, waits ~1000ms, executes event 2, waits ~1000ms, executes event 3, and signals completion

2. **Scenario**: Playback works on the active game window
   - **Given** a recorded macro exists and the game window is focused
   - **When** the user triggers playback
   - **Then** the mouse clicks and keyboard presses are delivered to the game window

---

### User Story 2 - Loop Playback (Priority: P2)

The user wants to loop the macro N times (or infinitely) so they can AFK-grind XP continuously without manual intervention.

**Why this priority**: Looping is what makes the app useful for extended grinding sessions. Single playback is the base; looping multiplies the value.

**Independent Test**: Create a macro, set loop count to 3, start playback. Verify the macro executes exactly 3 times in sequence.

**Acceptance Scenarios**:

1. **Scenario**: Fixed number of loops
   - **Given** a macro is stored in memory
   - **When** the user sets loop count to 5 and starts playback
   - **Then** the macro executes exactly 5 times, with a configurable delay between each loop

2. **Scenario**: Infinite loop
   - **Given** a macro is stored in memory
   - **When** the user sets loop count to "infinite" and starts playback
   - **Then** the macro repeats continuously until the user manually stops it

---

### User Story 3 - Stop Playback on Demand (Priority: P2)

The user needs to stop playback immediately at any point — if the loop count was set too high, or if something goes wrong in the game.

**Why this priority**: Without a reliable stop mechanism, the user has no control over a running macro.

**Independent Test**: Start a long/infinite loop playback, then trigger stop. Verify all input injection stops immediately and playback state is cleared.

**Acceptance Scenarios**:

1. **Scenario**: Stop during playback
   - **Given** a macro is currently being replayed
   - **When** the user triggers "stop playback"
   - **Then** all remaining events are skipped, no further input is injected, and the system exits playback state

---

### Edge Cases

- What happens if playback is triggered with no macro loaded? (should show an error or be disabled)
- What happens if playback is triggered while already playing? (should be ignored)
- What happens if the user switches windows during playback? (playback continues — input goes to the currently focused window, which is expected)
- What happens if a playback loop delay is set to 0? (no delay between loops — immediate restart)

## Requirements

### Functional Requirements

- **FR-001**: System MUST replay all recorded events in the correct order with their original relative timestamps.
- **FR-002**: System MUST inject mouse and keyboard events at the OS level (via pynput controllers).
- **FR-003**: System MUST support a configurable loop count (1 to N, plus infinite).
- **FR-004**: System MUST support a configurable delay between loop iterations.
- **FR-005**: System MUST allow playback to be stopped at any time.
- **FR-006**: System MUST signal playback state changes (playing, stopped, completed) to the frontend.
- **FR-007**: System MUST NOT inject input during the delay between loops.

### Key Entities

- **Playback Session**: Represents an active playback. Key attributes: `macro` (the macro being played), `loop_count`, `current_loop`, `delay_between_loops` (ms), `is_playing` (boolean), `current_event_index`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Playback timing is accurate to within 100ms of the original recording for macros under 60 seconds.
- **SC-002**: Stopping playback takes effect in under 500ms from trigger.
- **SC-003**: System supports at least 999 loop iterations without memory leaks or performance degradation.
- **SC-004**: Loop delay is consistent across iterations (within 50ms of the configured delay).
