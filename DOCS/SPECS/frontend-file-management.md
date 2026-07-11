# Feature Specification: File Management Panel (Frontend)

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Save a Recorded Macro (Priority: P1)

After recording a macro, the user types a name and clicks Save to persist it to disk. They can immediately see the saved macro appear in the list.

**Why this priority**: Saving is the first file operation users need after recording — without it, work is lost on app close.

**Independent Test**: Record a macro, type "orc-farm" in the name field, click Save. Verify the macro list updates to include "orc-farm".

**Acceptance Scenarios**:

1. **Scenario**: Save with a valid name
   - **Given** a macro is recorded (events > 0) and the name field contains "orc-farm"
   - **When** the user clicks "Save"
   - **Then** a success message appears, the macro list refreshes, and "orc-farm" appears in the dropdown

2. **Scenario**: Save with an empty name
   - **Given** the name field is empty
   - **When** the user clicks "Save"
   - **Then** an error message "Name cannot be empty" is shown

3. **Scenario**: Overwrite an existing macro
   - **Given** "orc-farm" already exists in the list
   - **When** the user saves a new macro with the same name
   - **Then** a confirmation prompt appears ("Overwrite existing macro?") — or the file is silently overwritten with a brief notice

---

### User Story 2 - Load a Saved Macro (Priority: P1)

The user selects a macro from the dropdown list and clicks Load. The macro's events are loaded into memory and ready for playback or editing.

**Why this priority**: Loading is the entry point for reusing previously saved macros across sessions.

**Independent Test**: Save a macro, select it from the dropdown, click Load. Verify the event count appears and the Play button enables.

**Acceptance Scenarios**:

1. **Scenario**: Load an existing macro
   - **Given** the dropdown contains at least 1 macro and "orc-farm" is selected
   - **When** the user clicks "Load"
   - **Then** the macro is loaded, the event count is displayed (e.g., "42 events loaded"), and the Play button enables

2. **Scenario**: Load with nothing selected
   - **Given** no macro is selected in the dropdown (empty state)
   - **When** the user clicks "Load"
   - **Then** an error message "Select a macro first" is shown

---

### User Story 3 - Delete a Macro (Priority: P2)

The user selects a macro from the list and clicks Delete to remove it permanently.

**Why this priority**: Housekeeping — users accumulate old macros and need to clean up.

**Independent Test**: Select "orc-farm" from the dropdown, click Delete, confirm the prompt. Verify it disappears from the list.

**Acceptance Scenarios**:

1. **Scenario**: Delete with confirmation
   - **Given** "orc-farm" is selected in the dropdown
   - **When** the user clicks "Delete" and confirms the prompt ("Are you sure?")
   - **Then** the macro file is deleted and removed from the list; if the deleted macro was the currently loaded one, the loaded macro is cleared

2. **Scenario**: Cancel deletion
   - **Given** "orc-farm" is selected
   - **When** the user clicks "Delete" but cancels the confirmation prompt
   - **Then** nothing is deleted and the list remains unchanged

---

### Edge Cases

- What if the dropdown is empty (no saved macros)? (show a placeholder message "No macros saved yet")
- What happens after deleting the currently loaded macro? (clear the loaded macro, disable Play button, show "No macro loaded")
- What if the backend returns a corrupted-macro error on load? (show the error message in the UI)
- What if the macros directory doesn't exist on first run? (handled by backend — frontend just shows empty list)

## Requirements

### Functional Requirements

- **FR-001**: The panel MUST display a text input for the macro name and a "Save" button.
- **FR-002**: The panel MUST display a dropdown/select listing all saved macros (fetched via `list_macros()`).
- **FR-003**: The panel MUST display a "Load" button that loads the selected macro.
- **FR-004**: The panel MUST display a "Delete" button with a confirmation prompt before deletion.
- **FR-005**: The macro list MUST refresh after every save, load, or delete operation.
- **FR-006**: The panel MUST show the loaded macro's event count after a successful load.

### Key Entities

- **Macro list**: Array of macro names (strings) from `list_macros()`.
- **Current macro**: The loaded macro name and event count.

## Success Criteria

- **SC-001**: Save and load operations provide feedback (success/error message) within 1 second.
- **SC-002**: The macro list is always up-to-date after any file operation.
- **SC-003**: Delete confirmation prevents accidental macro loss.
