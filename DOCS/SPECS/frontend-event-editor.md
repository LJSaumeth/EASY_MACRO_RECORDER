# Feature Specification: Event Editor Panel (Frontend)

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - View Recorded Events (Priority: P1)

After recording or loading a macro, the user sees a table listing all captured events: index, type (click/key/move), timestamp (ms), and details (button name, key name, coordinates). The table updates immediately after recording stops or a macro is loaded.

**Why this priority**: Viewing events is the prerequisite for all editing. Users must see what was captured before they can change it.

**Independent Test**: Record a macro with 3 events. Verify the table shows 3 rows with correct indices (0, 1, 2), types, timestamps, and details.

**Acceptance Scenarios**:

1. **Scenario**: Display events after recording
   - **Given** a macro with 5 events was just recorded
   - **When** recording stops
   - **Then** the event table shows 5 rows ordered by index with all columns populated

2. **Scenario**: Display events after loading
   - **Given** a saved macro is loaded from disk
   - **When** the load completes
   - **Then** the event table shows all loaded events

3. **Scenario**: Empty macro shows placeholder
   - **Given** no macro is loaded (0 events)
   - **When** the user views the Editor panel
   - **Then** the table area shows "No events to display" or an empty state message

---

### User Story 2 - Delete Individual Events (Priority: P2)

The user clicks a "Delete" button on a specific event row to remove it from the macro. The table updates immediately.

**Why this priority**: The most common editing action — removing accidental clicks or unwanted actions.

**Independent Test**: Load a macro with 3 events, click Delete on row 1. Verify row 1 disappears and the remaining events re-index (0, 1).

**Acceptance Scenarios**:

1. **Scenario**: Delete an event
   - **Given** the event table has 3 rows (indices 0, 1, 2)
   - **When** the user clicks the Delete button on row 1
   - **Then** row 1 is removed; the table now shows 2 rows (previously 0 and 2)

2. **Scenario**: Delete the last event
   - **Given** the event table has 1 row
   - **When** the user clicks Delete
   - **Then** the table becomes empty and shows the "No events" placeholder

---

### User Story 3 - Adjust Event Timing (Priority: P2)

The user enters a delta value (+ or -) in milliseconds next to an event row and clicks Apply to shift that event's timing (and all subsequent events).

**Why this priority**: Essential for fixing timing issues in recorded macros without re-recording.

**Independent Test**: Load a macro, adjust event 1's timestamp by +2000ms, click Apply. Verify the table updates and subsequent events shift accordingly.

**Acceptance Scenarios**:

1. **Scenario**: Increase delay before an event
   - **Given** event at index 1 has timestamp 3000ms
   - **When** the user enters "+2000" in the delta field and clicks Apply
   - **Then** event 1's timestamp becomes 5000ms and all later events also shift by +2000ms

2. **Scenario**: Decrease delay before an event
   - **Given** event at index 1 has timestamp 5000ms
   - **When** the user enters "-1000" and clicks Apply
   - **Then** event 1's timestamp becomes 4000ms and subsequent events shift back by 1000ms

---

### User Story 4 - Insert New Events (Priority: P3)

The user wants to add a new click, keypress, or pure delay at a specific position in the macro. They use an "Insert" form to pick the event type and position.

**Why this priority**: Power-user feature — most users re-record instead, but this saves time for small fixes.

**Independent Test**: Load a macro, click "Insert Event", fill in the form (type: mouse_click, x: 500, y: 300, position: 1), click Add. Verify a new row appears at position 1.

**Acceptance Scenarios**:

1. **Scenario**: Insert a mouse click event
   - **Given** a macro with 2 events
   - **When** the user inserts a "mouse_click" at index 1 with coordinates (500, 300) and button "left"
   - **Then** the table shows 3 events and the new event is at index 1

2. **Scenario**: Insert a delay (shift all subsequent timestamps)
   - **Given** a macro with 3 events
   - **When** the user inserts a delay of 5000ms at index 1
   - **Then** events at indices 1 and 2 have their timestamps increased by 5000ms

---

### Edge Cases

- What if the user tries to edit while recording or playback is active? (all edit controls should be disabled, table should be read-only)
- What if a timestamp delta causes negative timestamps? (backend clamps to 0 — frontend should reflect the clamped value after the operation)
- What if the table has thousands of rows? (should render without freezing — consider virtual scrolling or pagination if performance is a concern)
- What if the user deletes all events and then tries to Play? (Play button should be disabled since macro is empty)

## Requirements

### Functional Requirements

- **FR-001**: The panel MUST display an event table with columns: Index (#), Type, Timestamp (ms), Details.
- **FR-002**: Each event row MUST have a "Delete" button.
- **FR-003**: Each event row MUST have a delta input (+- ms) and an "Apply" button for timing adjustment.
- **FR-004**: The panel MUST include an "Insert Event" section with a form: event type dropdown, position index, and type-specific fields (x/y for mouse, key name for keyboard).
- **FR-005**: The panel MUST include an "Insert Delay" section: position index input and duration (ms) input.
- **FR-006**: The panel MUST include a "Clear All" button with a confirmation prompt.
- **FR-007**: All edit controls MUST be disabled when `can_edit` is False (recording or playback active).
- **FR-008**: The event table MUST refresh after every edit operation.

### Key Entities

- **Event row**: `index` (int), `event_type` (str), `timestamp` (int), `details` (str — concatenation of button/key/coordinates).

## Success Criteria

- **SC-001**: Event table renders 1,000 rows without noticeable UI lag.
- **SC-002**: All edit operations (delete, adjust, insert) provide visual feedback within 300ms.
- **SC-003**: Disabled state (grayed out controls) clearly communicates when editing is unavailable.
