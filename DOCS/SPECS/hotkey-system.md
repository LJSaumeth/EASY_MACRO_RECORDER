# Feature Specification: Hotkey System

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Start and Stop Recording via Hotkey (Priority: P1)

The user is inside their game (fullscreen or windowed) and wants to start/stop recording without alt-tabbing to the macro app. They press a configurable hotkey to toggle recording on and off.

**Why this priority**: The most critical hotkey — without it, the user must leave the game to control the app, breaking the recording workflow.

**Independent Test**: Set focus to Notepad (simulating a game), press the record hotkey, verify recording starts, type something, press the hotkey again, verify recording stops and events were captured.

**Acceptance Scenarios**:

1. **Scenario**: Toggle recording on with hotkey
   - **Given** the app is running and not recording, game window has focus
   - **When** the user presses the configured record hotkey (default: `F6`)
   - **Then** recording starts and a confirmation signal is sent to the frontend

2. **Scenario**: Toggle recording off with hotkey
   - **Given** the app is actively recording
   - **When** the user presses the record hotkey again
   - **Then** recording stops and all captured events are stored in memory

---

### User Story 2 - Start and Stop Playback via Hotkey (Priority: P1)

The user wants to trigger playback from within the game window — typically to start a grinding loop after positioning their character.

**Why this priority**: Equal priority to recording — the user needs hands-free access to both core functions.

**Independent Test**: Load a macro, focus on Notepad, press the playback hotkey, verify the macro replays. Press the hotkey again to stop.

**Acceptance Scenarios**:

1. **Scenario**: Start playback with hotkey
   - **Given** a macro is loaded in memory and the game window has focus
   - **When** the user presses the playback hotkey (default: `F7`)
   - **Then** the loaded macro begins replaying

2. **Scenario**: Stop playback with hotkey
   - **Given** a macro is currently being replayed
   - **When** the user presses the playback hotkey again (or the dedicated stop hotkey)
   - **Then** playback stops immediately

---

### User Story 3 - Emergency Stop Hotkey (Priority: P2)

The user needs a single panic button to stop ALL macro activity (both recording and playback) instantly — useful when something goes wrong and they need to regain control immediately.

**Why this priority**: Safety feature. While not used daily, it prevents frustration and potential issues in-game.

**Independent Test**: Start recording or playback, press the emergency stop hotkey, verify all activity stops immediately regardless of current state.

**Acceptance Scenarios**:

1. **Scenario**: Emergency stop during recording
   - **Given** the app is actively recording
   - **When** the user presses the emergency stop hotkey (default: `F8`)
   - **Then** recording stops immediately; any partially captured events are discarded or saved

2. **Scenario**: Emergency stop during playback
   - **Given** a macro is being replayed (loop count: infinite)
   - **When** the user presses the emergency stop hotkey
   - **Then** playback stops immediately; all input injection ceases

---

### User Story 4 - Hotkey Conflict Prevention (Priority: P3)

The user may configure hotkeys that conflict with in-game keybinds or system shortcuts. The system should warn or prevent such conflicts.

**Why this priority**: Nice-to-have for power users. Lower priority because sensible defaults cover most cases.

**Independent Test**: Attempt to configure a hotkey that conflicts with an existing one, verify the system warns about the conflict.

**Acceptance Scenarios**:

1. **Scenario**: Set a duplicate hotkey
   - **Given** F6 is already assigned to recording
   - **When** the user tries to assign F6 to playback
   - **Then** the system rejects the assignment and shows a conflict warning

---

### Edge Cases

- What happens if the configured hotkey is reserved by the OS (e.g., `Alt+F4`)? (prevent assignment of known system-reserved combinations)
- What happens when hotkeys are pressed while the app window is minimized? (global hotkeys should still work)
- What happens with modifier-based hotkeys (e.g., `Ctrl+Shift+F6`)? (should be supported, but the default should be single keys for simplicity)
- How does the system behave if two hotkey actions are triggered simultaneously? (process them sequentially; ignore duplicates)

## Requirements

### Functional Requirements

- **FR-001**: System MUST register global hotkeys that work when the app window does not have focus.
- **FR-002**: System MUST support a record toggle hotkey (default: `F6`).
- **FR-003**: System MUST support a playback toggle hotkey (default: `F7`).
- **FR-004**: System MUST support an emergency stop hotkey (default: `F8`).
- **FR-005**: System MUST allow users to reconfigure hotkeys (change the assigned key for each action).
- **FR-006**: System MUST prevent assigning the same hotkey to multiple actions.
- **FR-007**: System MUST prevent assigning known OS-reserved key combinations.
- **FR-008**: System MUST keep hotkey configuration persistent across app restarts (saved to a config file or integrated with macro persistence).

### Key Entities

- **Hotkey Binding**: Maps an action (`record`, `playback`, `stop`) to a key combination. Key attributes: `action`, `key_name`, `modifiers[]` (optional).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Hotkeys trigger their action within 200ms of keypress.
- **SC-002**: Global hotkeys work while any other application has focus, including fullscreen games.
- **SC-003**: Zero missed hotkey presses during normal operation.
- **SC-004**: Hotkey configuration changes take effect immediately without app restart.
