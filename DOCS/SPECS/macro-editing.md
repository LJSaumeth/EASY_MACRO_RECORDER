# Feature Specification: Macro Editing

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - View Recorded Events (Priority: P1)

After recording a macro, the user wants to see a list of all captured events — what actions were recorded, in what order, and with what timing — so they can verify and understand the macro before editing or playing it.

**Why this priority**: You can't edit what you can't see. Viewing is the prerequisite for all editing operations.

**Independent Test**: Record a macro with a click and a keypress, view the event list. Verify both events appear with their type, timestamp, and relevant details.

**Acceptance Scenarios**:

1. **Scenario**: View events of a recorded macro
   - **Given** a macro with 5 events is stored in memory
   - **When** the user views the event list
   - **Then** all 5 events are displayed in order with: event index, type (click/key), timestamp, and action details (button name, key name, coordinates)

2. **Scenario**: View events of an empty macro
   - **Given** a macro with 0 events is in memory
   - **When** the user views the event list
   - **Then** a message indicates the macro is empty

---

### User Story 2 - Delete Individual Events (Priority: P2)

While reviewing a macro, the user notices an accidental click at the end (e.g., clicking on the desktop after finishing the in-game loop). They want to remove that specific event without re-recording the entire macro.

**Why this priority**: The most common editing need — trimming unwanted events from the start or end of a recording.

**Independent Test**: Record a macro with 3 events, delete the last event, verify only 2 events remain with correct timing.

**Acceptance Scenarios**:

1. **Scenario**: Delete a specific event
   - **Given** a macro has events at indices 0, 1, 2
   - **When** the user deletes the event at index 1
   - **Then** events 0 and 2 remain; the list now has 2 events in correct order

2. **Scenario**: Delete the only event in a macro
   - **Given** a macro has 1 event
   - **When** the user deletes that event
   - **Then** the macro becomes empty (0 events)

3. **Scenario**: Delete with an out-of-bounds index
   - **Given** a macro has 3 events (indices 0-2)
   - **When** the user attempts to delete event at index 5
   - **Then** the system returns an error indicating the index is invalid

---

### User Story 3 - Adjust Event Timing (Priority: P2)

The user recorded a macro but one action happened too quickly (an attack went off before the cooldown was ready). They want to increase the delay before a specific event.

**Why this priority**: Timing adjustments are the second most common editing need after deleting events.

**Independent Test**: Record a macro, adjust the timestamp of event 2 by adding 2000ms. Play back and verify the extra delay is present.

**Acceptance Scenarios**:

1. **Scenario**: Increase the delay before an event
   - **Given** a macro has event at index 2 with a timestamp of 5000ms
   - **When** the user adds +2000ms to the timestamp of event 2
   - **Then** event 2's timestamp becomes 7000ms, and all subsequent events shift forward by 2000ms to preserve relative timing

2. **Scenario**: Decrease the delay before an event
   - **Given** a macro has event at index 1 with timestamp 3000ms, and event at index 0 with timestamp 0ms
   - **When** the user subtracts 1000ms from event 1's timestamp
   - **Then** event 1's timestamp becomes 2000ms and subsequent events adjust accordingly

3. **Scenario**: Reduce delay below zero
   - **Given** event 1 has timestamp 500ms
   - **When** the user tries to subtract 1000ms
   - **Then** the system clamps the timestamp to 0ms (minimum) or rejects the adjustment

---

### User Story 4 - Insert New Events Manually (Priority: P3)

The user wants to add a pause or an extra click into an existing macro without re-recording from scratch. For example, adding a 5-second wait between two actions to let a cooldown finish.

**Why this priority**: Convenience feature; most workflows use re-recording for complex changes, but this saves time for small tweaks.

**Independent Test**: Load a macro with 2 events, insert a new click event between them with a custom timestamp. Verify the event list has 3 events in the correct order.

**Acceptance Scenarios**:

1. **Scenario**: Insert a new event at a specific position
   - **Given** a macro has events at indices 0 and 1
   - **When** the user inserts a new mouse click event at index 1 with coordinates (500, 300)
   - **Then** the macro now has 3 events: original event 0, new click, original event 1; timestamps adjust accordingly

---

### Edge Cases

- What happens when the user deletes all events from a macro? (macro becomes empty — still valid)
- What happens when timestamp adjustments cause events to end up with identical timestamps? (should be allowed — events execute in their original order)
- What happens when inserting an event with an index beyond the list? (append at the end, or reject with error)
- What happens when editing a macro that is currently being played back? (editing should be disabled during active playback)

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide the full ordered list of recorded events to the frontend for display.
- **FR-002**: Each event in the list MUST include: index, type, timestamp, and type-specific data (key name, button, coordinates).
- **FR-003**: System MUST support deletion of individual events by index.
- **FR-004**: System MUST support adjusting the timestamp of individual events, automatically shifting subsequent event timestamps to preserve relative gaps.
- **FR-005**: System MUST support inserting new events (mouse clicks, key presses, delays) at any position in the event list.
- **FR-006**: System MUST prevent editing (delete, adjust, insert) while a macro is being recorded or played back.
- **FR-007**: System MUST signal event list changes to the frontend after each edit operation.

### Key Entities

- **Edit Operation**: Represents a change to a macro. Types: `delete_event(index)`, `adjust_timestamp(index, delta_ms)`, `insert_event(index, event)`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Event list for a macro with 1,000 events is returned to the frontend in under 500ms.
- **SC-002**: Deleting or adjusting any event completes in under 100ms.
- **SC-003**: Timestamp adjustments preserve relative gaps between events to within 1ms precision.
