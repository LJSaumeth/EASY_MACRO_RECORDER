from typing import Dict, List

from application.recording_service import RecordingService
from application.playback_service import PlaybackService
from application.persistence_service import PersistenceService
from application.hotkey_service import HotkeyService
from application.macro_editor import MacroEditor
from domain.exceptions import (
    CorruptedMacroError,
    EditingNotAllowedError,
    InvalidMacroNameError,
    MacroNotFoundError,
)


MAX_LOOP_COUNT = 999


class MacroApi:
    def __init__(
        self,
        recording_service: RecordingService,
        playback_service: PlaybackService,
        persistence_service: PersistenceService,
        hotkey_service: HotkeyService,
        macro_editor: MacroEditor,
    ):
        self._recording = recording_service
        self._playback = playback_service
        self._persistence = persistence_service
        self._hotkey = hotkey_service
        self._editor = macro_editor
        self._pending_events: List[Dict] = []

        self._recording.set_state_callback(self._on_state_event)
        self._playback.set_state_callback(self._on_state_event)

    def _on_state_event(self, event_type: str, data: dict) -> None:
        self._pending_events.append({"type": event_type, "data": data})

    def get_app_state(self) -> dict:
        is_recording = self._recording.is_recording()
        is_playing = self._playback.is_playing()
        playback_state = self._playback.get_state()
        can_edit = self._editor.can_edit()
        events = self._pending_events.copy()
        self._pending_events.clear()
        return {
            "is_recording": is_recording,
            "is_playing": is_playing,
            "playback": playback_state,
            "can_edit": can_edit,
            "events": events,
        }

    def start_recording(self) -> dict:
        return self._recording.start_recording()

    def stop_recording(self) -> dict:
        return self._recording.stop_recording()

    def get_macro_events(self) -> dict:
        try:
            events = self._editor.get_events()
        except EditingNotAllowedError:
            events = []
        serialized = [
            {
                "index": i,
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "button": e.button,
                "key": e.key,
                "x": e.x,
                "y": e.y,
            }
            for i, e in enumerate(events)
        ]
        return {"success": True, "events": serialized}

    def play_macro(self, loop_count: int = 1, delay_between_loops: int = 0) -> dict:
        if loop_count == -1:
            loop_count = -1
        elif loop_count < 1:
            loop_count = 1
        elif loop_count > MAX_LOOP_COUNT:
            loop_count = MAX_LOOP_COUNT
        return self._playback.play(
            loop_count=loop_count,
            delay_between_loops=delay_between_loops,
        )

    def stop_playback(self) -> dict:
        return self._playback.stop()

    def save_macro(self, name: str) -> dict:
        try:
            events = self._recording.get_current_macro()
            self._persistence.save_macro(name, events)
            macro = self._persistence.load_macro(name)
            self._playback.set_macro(macro.events)
            return {"success": True, "name": macro.name}
        except (InvalidMacroNameError, ValueError) as e:
            return {"success": False, "error": str(e)}

    def load_macro(self, name: str) -> dict:
        try:
            macro = self._persistence.load_macro(name)
            self._playback.set_macro(macro.events)
            return {
                "success": True,
                "name": macro.name,
                "event_count": len(macro.events),
            }
        except (MacroNotFoundError, CorruptedMacroError, InvalidMacroNameError) as e:
            return {"success": False, "error": str(e)}

    def list_macros(self) -> dict:
        macros = self._persistence.list_macros()
        return {"success": True, "macros": macros}

    def delete_macro(self, name: str) -> dict:
        try:
            self._persistence.delete_macro(name)
            return {"success": True}
        except (MacroNotFoundError, InvalidMacroNameError) as e:
            return {"success": False, "error": str(e)}

    def get_hotkeys(self) -> dict:
        bindings = self._hotkey.get_bindings()
        return {"success": True, "bindings": bindings}

    def set_hotkey(self, action: str, key: str) -> dict:
        return self._hotkey.set_hotkey(action, key)

    def reset_hotkeys_to_default(self) -> dict:
        return self._hotkey.reset_to_defaults()

    def delete_macro_event(self, index: int) -> dict:
        try:
            self._editor.delete_event(index)
            return {"success": True}
        except (IndexError, EditingNotAllowedError) as e:
            return {"success": False, "error": str(e)}

    def adjust_event_timestamp(self, index: int, delta_ms: int) -> dict:
        try:
            self._editor.adjust_timestamp(index, delta_ms)
            return {"success": True}
        except (IndexError, EditingNotAllowedError) as e:
            return {"success": False, "error": str(e)}

    def insert_macro_event(self, index: int, event_type: str, timestamp: int = 0,
                           button: str = "", key: str = "",
                           x: int = 0, y: int = 0) -> dict:
        from domain.models import MacroEvent
        try:
            event = MacroEvent(
                event_type=event_type,
                timestamp=timestamp,
                button=button if button else None,
                key=key if key else None,
                x=x if x else None,
                y=y if y else None,
            )
            self._editor.insert_event(index, event)
            return {"success": True}
        except (IndexError, EditingNotAllowedError) as e:
            return {"success": False, "error": str(e)}

    def insert_macro_delay(self, index: int, duration_ms: int) -> dict:
        try:
            self._editor.insert_delay(index, duration_ms)
            return {"success": True}
        except (IndexError, ValueError, EditingNotAllowedError) as e:
            return {"success": False, "error": str(e)}

    def clear_macro_events(self) -> dict:
        try:
            self._editor.clear_all_events()
            return {"success": True}
        except EditingNotAllowedError as e:
            return {"success": False, "error": str(e)}

    def can_edit_macro(self) -> dict:
        return {"success": True, "can_edit": self._editor.can_edit()}
