from typing import List

from domain.exceptions import InvalidMacroNameError
from domain.models import HotkeyBinding, HotkeyConfig
from infrastructure.hotkey_config_store import HotkeyConfigStore
from infrastructure.pynput_listener import GlobalHotkeyListener
from application.recording_service import RecordingService
from application.playback_service import PlaybackService


class HotkeyService:
    def __init__(
        self,
        listener: GlobalHotkeyListener,
        config_store: HotkeyConfigStore,
        recording_service: RecordingService,
        playback_service: PlaybackService,
    ):
        self._listener = listener
        self._config_store = config_store
        self._recording = recording_service
        self._playback = playback_service
        self._config: HotkeyConfig = HotkeyConfig.defaults()
        self._action_handlers = {
            "record_toggle": self._toggle_recording,
            "playback_toggle": self._toggle_playback,
            "emergency_stop": self._emergency_stop,
        }

    def initialize(self) -> None:
        self._config = self._config_store.load_config()
        self._register_all_bindings()
        self._listener.start()

    def shutdown(self) -> None:
        self._listener.clear_all()
        self._listener.stop()

    def set_hotkey(self, action: str, key: str, modifiers: List[str] = None) -> dict:
        if modifiers is None:
            modifiers = []
        if GlobalHotkeyListener.is_os_reserved(key, modifiers):
            return {"success": False, "error": "This key combination is reserved by the OS"}
        if self._find_conflicting(key, modifiers, exclude_action=action):
            return {"success": False, "error": "This key combination is already assigned"}
        for binding in self._config.bindings:
            if binding.action == action:
                self._listener.unregister_hotkey(binding)
                binding.key = key.lower()
                binding.modifiers = [m.lower() for m in modifiers]
                handler = self._action_handlers[action]
                self._listener.register_hotkey(binding, handler)
                self._config_store.save_config(self._config)
                return {"success": True}
        return {"success": False, "error": f"Unknown action: {action}"}

    def get_bindings(self) -> List[dict]:
        return [
            {"action": b.action, "key": b.key, "modifiers": b.modifiers}
            for b in self._config.bindings
        ]

    def reset_to_defaults(self) -> dict:
        self._listener.clear_all()
        self._config = HotkeyConfig.defaults()
        self._register_all_bindings()
        self._config_store.save_config(self._config)
        return {"success": True}

    def _register_all_bindings(self) -> None:
        self._listener.clear_all()
        for binding in self._config.bindings:
            handler = self._action_handlers.get(binding.action)
            if handler:
                self._listener.register_hotkey(binding, handler)

    def _toggle_recording(self) -> None:
        if self._recording.is_recording():
            self._recording.stop_recording()
        else:
            self._recording.start_recording()

    def _toggle_playback(self) -> None:
        if self._playback.is_playing():
            self._playback.stop()
        else:
            events = self._playback.get_current_macro()
            if events:
                self._playback.play(loop_count=1)

    def _emergency_stop(self) -> None:
        if self._recording.is_recording():
            self._recording.stop_recording()
        if self._playback.is_playing():
            self._playback.stop()

    def _find_conflicting(self, key: str, modifiers: List[str], exclude_action: str) -> bool:
        normalized_key = key.lower()
        normalized_mods = [m.lower() for m in modifiers]
        for binding in self._config.bindings:
            if binding.action == exclude_action:
                continue
            if binding.key.lower() == normalized_key and sorted(binding.modifiers) == sorted(normalized_mods):
                return True
        return False
