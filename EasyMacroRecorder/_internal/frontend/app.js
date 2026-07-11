"use strict";

let api;

const StatusBar = {
    dot: null,
    text: null,
    temp: null,
    tempTimeout: null,

    init() {
        this.dot = document.getElementById("status-indicator");
        this.text = document.getElementById("status-text");
        this.temp = document.getElementById("status-temp");
    },

    updateState(state) {
        this.dot.className = "status-dot";
        if (state.is_recording) {
            this.dot.classList.add("recording");
            this.text.textContent = "Recording...";
        } else if (state.is_playing) {
            this.dot.classList.add("playing");
            const pb = state.playback;
            const loopInfo = pb.loop_count === -1
                ? `Loop ${pb.current_loop} / ∞`
                : `Loop ${pb.current_loop} / ${pb.loop_count}`;
            this.text.textContent = `Playing (${loopInfo})`;
        } else {
            this.dot.classList.add("idle");
            this.text.textContent = "Ready";
        }
    },

    showMessage(msg, type) {
        clearTimeout(this.tempTimeout);
        this.temp.textContent = msg;
        this.temp.classList.remove("hidden");
        if (type === "error") {
            this.dot.className = "status-dot error";
        }
        this.tempTimeout = setTimeout(() => {
            this.temp.classList.add("hidden");
            this.dot.className = "status-dot";
        }, 3000);
    }
};

const RecordingPanel = {
    toggleBtn: null,
    eventCount: null,

    init() {
        this.toggleBtn = document.getElementById("rec-toggle-btn");
        this.eventCount = document.getElementById("rec-event-count");
        this.toggleBtn.addEventListener("click", () => this.toggleRecording());
    },

    updateState(state) {
        if (state.is_recording) {
            this.toggleBtn.textContent = "Stop Recording";
            this.toggleBtn.classList.add("recording");
        } else {
            this.toggleBtn.textContent = "Start Recording";
            this.toggleBtn.classList.remove("recording");
        }
        this.toggleBtn.disabled = state.is_playing;
    },

    showEventCount(count) {
        if (count > 0) {
            this.eventCount.textContent = `${count} events captured`;
            this.eventCount.classList.remove("hidden");
        }
    },

    hideEventCount() {
        this.eventCount.classList.add("hidden");
    },

    async toggleRecording() {
        try {
            if (this.toggleBtn.classList.contains("recording")) {
                const result = await api.stop_recording();
                if (result.success) {
                    this.showEventCount(result.event_count);
                    StatusBar.showMessage(`Recording stopped — ${result.event_count} events`, "success");
                }
            } else {
                this.hideEventCount();
                const result = await api.start_recording();
                if (!result.success && result.error) {
                    StatusBar.showMessage(result.error, "error");
                }
            }
        } catch (e) {
            StatusBar.showMessage("API error: " + e, "error");
        }
    }
};

const PlaybackPanel = {
    toggleBtn: null,
    loopCount: null,
    loopInfinite: null,
    loopDelay: null,
    progress: null,

    init() {
        this.toggleBtn = document.getElementById("play-toggle-btn");
        this.loopCount = document.getElementById("loop-count");
        this.loopInfinite = document.getElementById("loop-infinite");
        this.loopDelay = document.getElementById("loop-delay");
        this.progress = document.getElementById("play-progress");

        this.toggleBtn.addEventListener("click", () => this.togglePlayback());
        this.loopInfinite.addEventListener("change", () => this.onInfiniteToggle());
        this.loopCount.addEventListener("blur", () => this.validateLoopCount());
        this.loopDelay.addEventListener("blur", () => this.validateDelay());
    },

    updateState(state) {
        const hasEvents = state.playback && state.playback.total_events > 0;
        if (state.is_playing) {
            this.toggleBtn.textContent = "Stop";
            this.toggleBtn.classList.add("playing");
            this.toggleBtn.disabled = false;
            const pb = state.playback;
            const loopMsg = pb.loop_count === -1
                ? `${pb.current_loop} / ∞`
                : `${pb.current_loop} / ${pb.loop_count}`;
            this.progress.textContent = `Event ${pb.current_event_index + 1}/${pb.total_events} | Loop ${loopMsg}`;
            this.progress.classList.remove("hidden");
        } else {
            this.toggleBtn.textContent = "Play";
            this.toggleBtn.classList.remove("playing");
            this.toggleBtn.disabled = state.is_recording || !hasEvents;
            this.progress.classList.add("hidden");
        }
    },

    onInfiniteToggle() {
        this.loopCount.disabled = this.loopInfinite.checked;
        if (this.loopInfinite.checked) {
            this.loopCount.value = "∞";
        } else {
            this.loopCount.value = "1";
        }
    },

    validateLoopCount() {
        if (this.loopInfinite.checked) return;
        let val = parseInt(this.loopCount.value, 10);
        if (isNaN(val) || val < 1) val = 1;
        if (val > 999) val = 999;
        this.loopCount.value = val;
    },

    validateDelay() {
        let val = parseInt(this.loopDelay.value, 10);
        if (isNaN(val) || val < 0) val = 0;
        this.loopDelay.value = val;
    },

    async togglePlayback() {
        try {
            if (this.toggleBtn.classList.contains("playing")) {
                const result = await api.stop_playback();
                if (result.success) {
                    StatusBar.showMessage("Playback stopped", "info");
                }
            } else {
                const count = this.loopInfinite.checked ? -1 : parseInt(this.loopCount.value, 10) || 1;
                const delay = parseInt(this.loopDelay.value, 10) || 0;
                const result = await api.play_macro(count, delay);
                if (!result.success && result.error) {
                    StatusBar.showMessage(result.error, "error");
                }
            }
        } catch (e) {
            StatusBar.showMessage("API error: " + e, "error");
        }
    }
};

const FilePanel = {
    nameInput: null,
    saveBtn: null,
    macroList: null,
    loadBtn: null,
    deleteBtn: null,
    info: null,
    loadedMacroName: null,

    init() {
        this.nameInput = document.getElementById("macro-name");
        this.saveBtn = document.getElementById("save-btn");
        this.macroList = document.getElementById("macro-list");
        this.loadBtn = document.getElementById("load-btn");
        this.deleteBtn = document.getElementById("delete-btn");
        this.info = document.getElementById("file-info");

        this.saveBtn.addEventListener("click", () => this.saveMacro());
        this.loadBtn.addEventListener("click", () => this.loadMacro());
        this.deleteBtn.addEventListener("click", () => this.deleteMacro());
    },

    updateState(state) {
    },

    async saveMacro() {
        const name = this.nameInput.value.trim();
        if (!name) {
            StatusBar.showMessage("Please enter a macro name", "error");
            return;
        }
        try {
            const result = await api.save_macro(name);
            if (result.success) {
                StatusBar.showMessage(`Macro "${result.name}" saved`, "success");
                this.loadedMacroName = result.name;
                this.showLoadedInfo(result.name);
                await this.refreshMacroList();
                AppController.notifyMacroLoaded();
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Save failed: " + e, "error");
        }
    },

    async loadMacro() {
        const name = this.macroList.value;
        if (!name) {
            StatusBar.showMessage("Select a macro to load", "error");
            return;
        }
        try {
            const result = await api.load_macro(name);
            if (result.success) {
                this.loadedMacroName = result.name;
                this.showLoadedInfo(result.name, result.event_count);
                StatusBar.showMessage(`Loaded "${result.name}" (${result.event_count} events)`, "success");
                AppController.notifyMacroLoaded();
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Load failed: " + e, "error");
        }
    },

    async deleteMacro() {
        const name = this.macroList.value;
        if (!name) {
            StatusBar.showMessage("Select a macro to delete", "error");
            return;
        }
        if (!confirm(`Delete macro "${name}"?`)) return;
        try {
            const result = await api.delete_macro(name);
            if (result.success) {
                StatusBar.showMessage(`Deleted "${name}"`, "info");
                if (this.loadedMacroName === name) {
                    this.clearLoadedInfo();
                }
                await this.refreshMacroList();
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Delete failed: " + e, "error");
        }
    },

    async refreshMacroList() {
        try {
            const result = await api.list_macros();
            this.macroList.innerHTML = "";
            if (result.macros && result.macros.length > 0) {
                result.macros.forEach(name => {
                    const opt = document.createElement("option");
                    opt.value = name;
                    opt.textContent = name;
                    this.macroList.appendChild(opt);
                });
            } else {
                const opt = document.createElement("option");
                opt.disabled = true;
                opt.selected = true;
                opt.textContent = "No macros saved yet";
                this.macroList.appendChild(opt);
            }
        } catch (e) {
            StatusBar.showMessage("List failed: " + e, "error");
        }
    },

    showLoadedInfo(name, count) {
        this.info.textContent = count !== undefined
            ? `Loaded: ${name} (${count} events)`
            : `Loaded: ${name}`;
        this.info.classList.remove("hidden");
    },

    clearLoadedInfo() {
        this.info.classList.add("hidden");
        this.loadedMacroName = null;
    }
};

const EditorPanel = {
    tableBody: null,
    emptyMsg: null,
    wrapper: null,
    insertEventType: null,
    insertPos: null,
    insertMouseFields: null,
    insertKeyField: null,
    insertX: null,
    insertY: null,
    insertButton: null,
    insertKey: null,
    insertEventBtn: null,
    delayPos: null,
    delayDuration: null,
    insertDelayBtn: null,
    clearBtn: null,
    previousRecording: false,

    init() {
        this.tableBody = document.querySelector("#event-table tbody");
        this.emptyMsg = document.getElementById("editor-empty-msg");
        this.wrapper = document.getElementById("editor-panel");
        this.insertEventType = document.getElementById("insert-event-type");
        this.insertPos = document.getElementById("insert-pos");
        this.insertMouseFields = document.getElementById("insert-mouse-fields");
        this.insertKeyField = document.getElementById("insert-key-field");
        this.insertX = document.getElementById("insert-x");
        this.insertY = document.getElementById("insert-y");
        this.insertButton = document.getElementById("insert-button");
        this.insertKey = document.getElementById("insert-key");
        this.insertEventBtn = document.getElementById("insert-event-btn");
        this.delayPos = document.getElementById("delay-pos");
        this.delayDuration = document.getElementById("delay-duration");
        this.insertDelayBtn = document.getElementById("insert-delay-btn");
        this.clearBtn = document.getElementById("clear-events-btn");

        this.insertEventType.addEventListener("change", () => this.toggleInsertFields());
        this.insertEventBtn.addEventListener("click", () => this.insertEvent());
        this.insertDelayBtn.addEventListener("click", () => this.insertDelay());
        this.clearBtn.addEventListener("click", () => this.clearAll());
    },

    updateState(state) {
        if (state.can_edit) {
            this.wrapper.classList.remove("editor-disabled");
        } else {
            this.wrapper.classList.add("editor-disabled");
        }
        if (this.previousRecording && !state.is_recording) {
            this.refreshTable();
        }
        this.previousRecording = state.is_recording;
    },

    async refreshTable() {
        try {
            const result = await api.get_macro_events();
            this.tableBody.innerHTML = "";
            if (!result.events || result.events.length === 0) {
                this.emptyMsg.classList.remove("hidden");
                return;
            }
            this.emptyMsg.classList.add("hidden");
            result.events.forEach(evt => {
                const tr = document.createElement("tr");
                tr.dataset.index = evt.index;

                const idxTd = document.createElement("td");
                idxTd.textContent = evt.index;
                tr.appendChild(idxTd);

                const typeTd = document.createElement("td");
                typeTd.textContent = evt.event_type;
                tr.appendChild(typeTd);

                const timeTd = document.createElement("td");
                timeTd.textContent = evt.timestamp;
                tr.appendChild(timeTd);

                const detailsTd = document.createElement("td");
                detailsTd.textContent = EditorPanel.formatDetails(evt);
                tr.appendChild(detailsTd);

                const deleteTd = document.createElement("td");
                const delBtn = document.createElement("button");
                delBtn.textContent = "Del";
                delBtn.className = "event-row-delete";
                delBtn.addEventListener("click", () => EditorPanel.deleteEvent(evt.index));
                deleteTd.appendChild(delBtn);
                tr.appendChild(deleteTd);

                const adjustTd = document.createElement("td");
                const adjustInput = document.createElement("input");
                adjustInput.type = "number";
                adjustInput.className = "event-adjust-input";
                adjustInput.value = "0";
                const applyBtn = document.createElement("button");
                applyBtn.textContent = "Apply";
                applyBtn.className = "event-adjust-btn";
                applyBtn.addEventListener("click", () => {
                    const delta = parseInt(adjustInput.value, 10) || 0;
                    EditorPanel.adjustTimestamp(evt.index, delta);
                });
                adjustTd.appendChild(adjustInput);
                adjustTd.appendChild(applyBtn);
                tr.appendChild(adjustTd);

                this.tableBody.appendChild(tr);
            });
        } catch (e) {
            StatusBar.showMessage("Failed to load events: " + e, "error");
        }
    },

    async deleteEvent(index) {
        try {
            const result = await api.delete_macro_event(index);
            if (result.success) {
                this.refreshTable();
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Delete failed: " + e, "error");
        }
    },

    async adjustTimestamp(index, delta) {
        if (delta === 0) return;
        try {
            const result = await api.adjust_event_timestamp(index, delta);
            if (result.success) {
                this.refreshTable();
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Adjust failed: " + e, "error");
        }
    },

    async insertEvent() {
        const eventType = this.insertEventType.value;
        const pos = parseInt(this.insertPos.value, 10) || 0;
        try {
            let button = "";
            let key = "";
            let x = 0;
            let y = 0;
            if (eventType === "mouse_click" || eventType === "mouse_move") {
                x = parseInt(this.insertX.value, 10) || 0;
                y = parseInt(this.insertY.value, 10) || 0;
                if (eventType === "mouse_click") {
                    button = this.insertButton.value;
                }
            } else {
                key = this.insertKey.value.trim();
                if (!key) {
                    StatusBar.showMessage("Please enter a key name", "error");
                    return;
                }
            }
            const result = await api.insert_macro_event(pos, eventType, 0, button, key, x, y);
            if (result.success) {
                this.refreshTable();
                StatusBar.showMessage("Event inserted", "success");
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Insert failed: " + e, "error");
        }
    },

    async insertDelay() {
        const pos = parseInt(this.delayPos.value, 10) || 0;
        const duration = parseInt(this.delayDuration.value, 10) || 1000;
        if (duration <= 0) {
            StatusBar.showMessage("Duration must be positive", "error");
            return;
        }
        try {
            const result = await api.insert_macro_delay(pos, duration);
            if (result.success) {
                this.refreshTable();
                StatusBar.showMessage(`Delay of ${duration}ms inserted`, "success");
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Delay insert failed: " + e, "error");
        }
    },

    async clearAll() {
        if (!confirm("Clear all events from the current macro?")) return;
        try {
            const result = await api.clear_macro_events();
            if (result.success) {
                this.refreshTable();
                StatusBar.showMessage("All events cleared", "info");
            } else {
                StatusBar.showMessage(result.error, "error");
            }
        } catch (e) {
            StatusBar.showMessage("Clear failed: " + e, "error");
        }
    },

    toggleInsertFields() {
        const type = this.insertEventType.value;
        const isMouse = type === "mouse_click" || type === "mouse_move";
        this.insertMouseFields.classList.toggle("hidden", !isMouse);
        this.insertKeyField.classList.toggle("hidden", isMouse);
    },

    formatDetails(evt) {
        switch (evt.event_type) {
            case "mouse_click":
                return `${evt.button || "?"} @ (${evt.x ?? "?"}, ${evt.y ?? "?"})`;
            case "mouse_move":
                return `move to (${evt.x ?? "?"}, ${evt.y ?? "?"})`;
            case "key_press":
                return `press "${evt.key || "?"}"`;
            case "key_release":
                return `release "${evt.key || "?"}"`;
            default:
                return evt.event_type;
        }
    }
};

const HotkeyPanel = {
    tableBody: null,
    error: null,
    resetBtn: null,
    overlay: null,
    capturePrompt: null,
    captureTimeoutEl: null,
    captureTargetAction: null,
    captureTimer: null,
    captureSeconds: 0,

    init() {
        this.tableBody = document.querySelector("#hotkey-table tbody");
        this.error = document.getElementById("hotkey-error");
        this.resetBtn = document.getElementById("reset-hotkeys-btn");
        this.overlay = document.getElementById("key-capture-overlay");
        this.capturePrompt = document.getElementById("capture-prompt");
        this.captureTimeoutEl = document.getElementById("capture-timeout");

        this.tableBody.addEventListener("click", (e) => {
            const btn = e.target.closest(".hotkey-change-btn");
            if (btn) {
                this.startKeyCapture(btn.dataset.action);
            }
        });
        this.resetBtn.addEventListener("click", () => this.resetToDefaults());
    },

    updateState(state) {
        this.resetBtn.disabled = state.is_recording || state.is_playing;
    },

    async refreshBindingsTable() {
        try {
            const result = await api.get_hotkeys();
            if (!result.bindings) return;
            this.tableBody.innerHTML = "";
            this.error.classList.add("hidden");
            const actionLabels = {
                record_toggle: "Record Toggle",
                playback_toggle: "Playback Toggle",
                emergency_stop: "Emergency Stop",
            };
            result.bindings.forEach(b => {
                const tr = document.createElement("tr");
                const actionTd = document.createElement("td");
                actionTd.textContent = actionLabels[b.action] || b.action;
                tr.appendChild(actionTd);

                const keyTd = document.createElement("td");
                keyTd.textContent = b.key.toUpperCase();
                tr.appendChild(keyTd);

                const btnTd = document.createElement("td");
                const btn = document.createElement("button");
                btn.textContent = "Change";
                btn.className = "hotkey-change-btn";
                btn.dataset.action = b.action;
                btnTd.appendChild(btn);
                tr.appendChild(btnTd);

                this.tableBody.appendChild(tr);
            });
        } catch (e) {
            StatusBar.showMessage("Failed to load hotkeys: " + e, "error");
        }
    },

    startKeyCapture(action) {
        this.captureTargetAction = action;
        this.overlay.classList.remove("hidden");
        this.captureSeconds = 5;
        this.captureTimeoutEl.textContent = "5";
        this.captureTimer = setInterval(() => this.tickCapture(), 1000);
        document.addEventListener("keydown", this.onKeyCaptured, { once: true });
    },

    tickCapture() {
        this.captureSeconds--;
        this.captureTimeoutEl.textContent = String(this.captureSeconds);
        if (this.captureSeconds <= 0) {
            this.cancelCapture();
        }
    },

    onKeyCaptured(event) {
        if (event && event.preventDefault) event.preventDefault();
        clearInterval(HotkeyPanel.captureTimer);
        document.removeEventListener("keydown", HotkeyPanel.onKeyCaptured);
        HotkeyPanel.overlay.classList.add("hidden");
        const keyName = HotkeyPanel.normalizeKeyName(event);
        HotkeyPanel.submitRebind(HotkeyPanel.captureTargetAction, keyName);
        HotkeyPanel.captureTargetAction = null;
    },

    cancelCapture() {
        clearInterval(this.captureTimer);
        document.removeEventListener("keydown", this.onKeyCaptured);
        this.overlay.classList.add("hidden");
        this.captureTargetAction = null;
    },

    async submitRebind(action, key) {
        try {
            const result = await api.set_hotkey(action, key);
            if (result.success) {
                await this.refreshBindingsTable();
                StatusBar.showMessage(`Hotkey updated: ${key.toUpperCase()}`, "success");
            } else {
                this.error.textContent = result.error || "Failed to set hotkey";
                this.error.classList.remove("hidden");
                setTimeout(() => this.error.classList.add("hidden"), 4000);
            }
        } catch (e) {
            StatusBar.showMessage("Rebind failed: " + e, "error");
        }
    },

    async resetToDefaults() {
        if (!confirm("Reset all hotkeys to default (F6, F7, F8)?")) return;
        try {
            const result = await api.reset_hotkeys_to_default();
            if (result.success) {
                await this.refreshBindingsTable();
                StatusBar.showMessage("Hotkeys reset to defaults", "success");
            }
        } catch (e) {
            StatusBar.showMessage("Reset failed: " + e, "error");
        }
    },

    normalizeKeyName(event) {
        if (event.code && event.code.startsWith("Key")) {
            return event.code.replace("Key", "").toLowerCase();
        }
        if (event.code && event.code.startsWith("Digit")) {
            return event.code.replace("Digit", "");
        }
        if (event.key === " ") return "space";
        if (event.key.length === 1) return event.key;
        const codeMap = {
            "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
            "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8",
            "F9": "f9", "F10": "f10", "F11": "f11", "F12": "f12",
            "Escape": "esc", "Enter": "enter", "Tab": "tab",
            "Backspace": "backspace", "Delete": "delete", " ": "space",
            "ArrowUp": "up", "ArrowDown": "down",
            "ArrowLeft": "left", "ArrowRight": "right",
        };
        return codeMap[event.key] || codeMap[event.code] || event.key.toLowerCase();
    }
};

const AppController = {
    pollingInterval: null,
    previousState: null,

    async init() {
        StatusBar.init();
        RecordingPanel.init();
        PlaybackPanel.init();
        FilePanel.init();
        EditorPanel.init();
        HotkeyPanel.init();

        await FilePanel.refreshMacroList();
        await HotkeyPanel.refreshBindingsTable();

        this.startPolling();
    },

    startPolling() {
        this.pollingInterval = setInterval(() => this.pollState(), 500);
        this.pollState();
    },

    async pollState() {
        try {
            const state = await api.get_app_state();
            this.processEvents(state.events);
            StatusBar.updateState(state);
            RecordingPanel.updateState(state);
            PlaybackPanel.updateState(state);
            FilePanel.updateState(state);
            EditorPanel.updateState(state);
            HotkeyPanel.updateState(state);
            this.previousState = state;
        } catch (e) {
            if (e.message && e.message.includes("not defined")) {
                return;
            }
            StatusBar.showMessage("Polling error: " + e, "error");
        }
    },

    processEvents(events) {
        if (!events || events.length === 0) return;
        events.forEach(evt => {
            switch (evt.type) {
                case "playback_completed":
                    StatusBar.showMessage("Playback completed", "success");
                    break;
            }
        });
    },

    notifyMacroLoaded() {
        EditorPanel.refreshTable();
    }
};

window.addEventListener("pywebviewready", () => {
    api = window.pywebview.api;
    AppController.init();
});
