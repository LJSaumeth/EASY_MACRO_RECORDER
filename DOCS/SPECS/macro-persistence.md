# Feature Specification: Macro Persistence

**Created**: 2026-07-11

## User Scenarios & Testing

### User Story 1 - Save a Macro to a JSON File (Priority: P1)

After recording a macro, the user wants to save it permanently so they can reuse it across sessions without re-recording.

**Why this priority**: Without persistence, macros are lost when the app closes. Saving is the most essential file operation.

**Independent Test**: Record a macro, save it with a name, close the app, reopen it, and verify the macro file exists in the `macros/` directory.

**Acceptance Scenarios**:

1. **Scenario**: Save a new macro
   - **Given** a recorded macro is in memory
   - **When** the user saves it with the name "orc-grinding"
   - **Then** a file `macros/orc-grinding.json` is created containing the full event list with timestamps

2. **Scenario**: Overwrite an existing macro
   - **Given** a macro named "orc-grinding" already exists on disk
   - **When** the user saves a macro with the same name
   - **Then** the existing file is overwritten with the new macro data

3. **Scenario**: Save with special characters in name
   - **Given** a recorded macro is in memory
   - **When** the user attempts to save with a name containing invalid filename characters (e.g., `/`, `\`, `:`)
   - **Then** the system rejects the name and shows an appropriate error message

---

### User Story 2 - Load a Macro from a JSON File (Priority: P1)

The user opens the app, wants to load a previously saved macro so they can play it back without re-recording.

**Why this priority**: Loading is the counterpart to saving. Together they form the complete persistence loop.

**Independent Test**: Ensure a macro file exists, load it by name, verify the macro is in memory and ready for playback.

**Acceptance Scenarios**:

1. **Scenario**: Load an existing macro
   - **Given** a valid macro file `macros/orc-grinding.json` exists
   - **When** the user loads "orc-grinding"
   - **Then** the macro is loaded into memory and its event count is reported to the frontend

2. **Scenario**: Load a non-existent macro
   - **Given** no file exists for the requested name
   - **When** the user attempts to load "nonexistent"
   - **Then** the system returns an error indicating the macro was not found

3. **Scenario**: Load a corrupted macro file
   - **Given** a file exists but contains invalid JSON or an unrecognized schema
   - **When** the user attempts to load it
   - **Then** the system returns an error indicating the file is corrupted

---

### User Story 3 - List All Saved Macros (Priority: P2)

The user wants to browse all their saved macros to decide which one to load or delete.

**Why this priority**: Listing is a convenience feature that enables the full file management workflow.

**Independent Test**: Save 3 macros with different names, request the macro list, verify all 3 appear.

**Acceptance Scenarios**:

1. **Scenario**: List macros when files exist
   - **Given** the `macros/` directory contains 3 .json macro files
   - **When** the user requests the macro list
   - **Then** an array of 3 macro names (without extensions) is returned

2. **Scenario**: List macros when directory is empty
   - **Given** the `macros/` directory exists but contains no .json macro files
   - **When** the user requests the macro list
   - **Then** an empty list is returned

3. **Scenario**: List macros ignores non-macro files
   - **Given** the `macros/` directory contains macro files and other files (e.g., `notes.txt`)
   - **When** the user requests the macro list
   - **Then** only .json macro files are returned; non-.json files are ignored

---

### User Story 4 - Delete a Saved Macro (Priority: P3)

The user wants to clean up old or unwanted macros.

**Why this priority**: Delete is lower priority than save/load but completes the CRUD set.

**Independent Test**: Save a macro, delete it by name, verify the file is removed and no longer appears in the list.

**Acceptance Scenarios**:

1. **Scenario**: Delete an existing macro
   - **Given** `macros/orc-grinding.json` exists
   - **When** the user deletes "orc-grinding"
   - **Then** the file is permanently removed from the `macros/` directory

2. **Scenario**: Delete a non-existent macro
   - **Given** no file exists for the requested name
   - **When** the user attempts to delete "nonexistent"
   - **Then** the system returns an error indicating the macro was not found

---

### Edge Cases

- What happens when the `macros/` directory doesn't exist on startup? (system should create it automatically)
- What happens when saving a macro with an empty event list? (should still save — a valid empty macro for future editing)
- What happens when two macros have the same name but different casing? (treat them as the same — case-insensitive comparison to avoid confusion)
- What happens when the disk is full during save? (return a clear error, keep the in-memory macro intact)

## Requirements

### Functional Requirements

- **FR-001**: System MUST serialize macros to .json files in the `macros/` directory.
- **FR-002**: System MUST deserialize macros from .json files into in-memory macro objects.
- **FR-003**: System MUST list all .json macro files in the `macros/` directory.
- **FR-004**: System MUST delete specified macro files from the `macros/` directory.
- **FR-005**: System MUST create the `macros/` directory on startup if it does not exist.
- **FR-006**: System MUST validate JSON structure when loading macros and reject corrupted files with a clear error.
- **FR-007**: Macro filenames MUST be sanitized — only alphanumeric characters, hyphens, and underscores allowed.
- **FR-008**: System MUST handle filesystem errors gracefully (disk full, permission denied) and return descriptive errors to the frontend.

### Key Entities

- **Macro File**: A .json file in the `macros/` directory. Contains a serialized `Macro` object. Key attributes: `name` (derived from filename), `events[]`, `created_at`, `updated_at`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Saving or loading a macro with up to 5,000 events completes in under 1 second.
- **SC-002**: Listing macros completes in under 200ms regardless of directory size.
- **SC-003**: Corrupted files are detected and error messages displayed without crashing the app.
- **SC-004**: All file operations leave the macro directory in a consistent state (no partial writes).
