# Feature Specification: Hotkey Configuration Panel (Frontend)

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - View Current Hotkey Bindings (Priority: P1)

The user wants to see which keys are assigned to which actions so they know what hotkeys are available when they're in-game.

**Why this priority**: Users must know their current hotkeys before they can use them effectively.

**Independent Test**: Open the app, navigate to the Hotkeys panel. Verify the table shows Record = F6, Playback = F7, Emergency Stop = F8.

**Acceptance Scenarios**:

1. **Scenario**: Display default bindings
   - **Given** the app is freshly installed with no custom hotkey config
   - **When** the user views the Hotkeys panel
   - **Then** a table shows: Record Toggle → F6, Playback Toggle → F7, Emergency Stop → F8

2. **Scenario**: Display custom bindings
   - **Given** the user previously changed the record hotkey to F9
   - **When** the user opens the app and views the Hotkeys panel
   - **Then** the table shows Record Toggle → F9

---

### User Story 2 - Change a Hotkey Binding (Priority: P2)

The user wants to reassign the record hotkey to F9 because F6 is used by their game. They click the Change button for "Record Toggle", press F9, and the binding updates.

**Why this priority**: Default hotkeys may conflict with in-game binds. Customization is essential for usability.

**Independent Test**: Click Change on Record Toggle, press F9 in the capture prompt. Verify the table updates to show F9 and the change persists after app restart.

**Acceptance Scenarios**:

1. **Scenario**: Rebind a hotkey successfully
   - **Given** the Hotkeys panel is open and the user clicks "Change" on Record Toggle
   - **When** a capture prompt appears, the user presses F9, and the binding is saved
   - **Then** the table updates to show F9 for Record Toggle, and the new binding takes effect immediately

2. **Scenario**: Attempt to assign a conflicting key
   - **Given** F7 is already assigned to Playback Toggle
   - **When** the user tries to assign F7 to Record Toggle
   - **Then** an error message "This key is already assigned to Playback Toggle" is shown

3. **Scenario**: Attempt to assign an OS-reserved key
   - **Given** the user clicks Change and presses Alt+F4
   - **When** the binding is submitted
   - **Then** an error message "This combination is reserved by the OS" is shown

---

### User Story 3 - Reset Hotkeys to Defaults (Priority: P3)

The user has customized hotkeys and wants to revert to the default F6/F7/F8 configuration.

**Why this priority**: Convenience for recovery from a problematic configuration.

**Independent Test**: Change Record to F9, click "Reset to Defaults". Verify all three bindings return to F6/F7/F8.

**Acceptance Scenarios**:

1. **Scenario**: Reset all bindings
   - **Given** hotkeys have been customized (e.g., F9, F10, F11)
   - **When** the user clicks "Reset to Defaults"
   - **Then** the table returns to F6/F7/F8 and the changes are persisted

---

### Edge Cases

- What if the backend returns an error during rebind? (show the error message from the API response)
- What if the hotkey config file is corrupted? (backend returns defaults — frontend displays them normally)
- What happens during the "press a key" capture mode — should it timeout? (yes, after 5 seconds of no input, cancel the capture and revert)

## Requirements

### Functional Requirements

- **FR-001**: The panel MUST display a table with columns: Action, Current Key, and a "Change" button per row.
- **FR-002**: The "Change" button MUST open a key capture mode that listens for a single keypress and submits it.
- **FR-003**: The capture mode MUST show a visual indicator (e.g., "Press a key...") and timeout after 5 seconds.
- **FR-004**: The panel MUST show error messages from the API (conflicts, OS-reserved keys).
- **FR-005**: The panel MUST include a "Reset to Defaults" button with a confirmation prompt.
- **FR-006**: The table MUST refresh after any successful rebind or reset.

### Key Entities

- **Hotkey binding**: `action` (str), `key` (str).

## Success Criteria

- **SC-001**: Key capture starts within 200ms of clicking "Change".
- **SC-002**: Capture timeout (5s) is clearly communicated to the user.
- **SC-003**: Hotkey changes are immediately usable without app restart.
