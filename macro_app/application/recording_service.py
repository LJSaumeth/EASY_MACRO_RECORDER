from typing import Callable, List, Optional

from domain.models import MacroEvent, RecordingSession
from infrastructure.pynput_listener import PynputListener


class RecordingService:
    def __init__(self, listener: PynputListener):
        self._listener = listener
        self._session = RecordingSession()
        self._on_state_changed: Optional[Callable[[str, dict], None]] = None

    def set_state_callback(self, callback: Callable[[str, dict], None]) -> None:
        self._on_state_changed = callback

    def start_recording(self) -> dict:
        if self._session.is_recording:
            return {"success": False, "error": "Already recording"}
        self._session = RecordingSession(is_recording=True)
        self._listener.start_listening(self._on_event_captured)
        self._notify("recording_started", {})
        return {"success": True}

    def stop_recording(self) -> dict:
        if not self._session.is_recording:
            return {"success": False, "error": "Not recording"}
        self._listener.stop_listening()
        self._session.is_recording = False
        event_count = len(self._session.events)
        self._notify("recording_stopped", {"event_count": event_count})
        return {"success": True, "event_count": event_count}

    def get_current_macro(self) -> List[MacroEvent]:
        return list(self._session.events)

    def is_recording(self) -> bool:
        return self._session.is_recording

    def _on_event_captured(self, event: MacroEvent) -> None:
        self._session.events.append(event)

    def _notify(self, event_type: str, data: dict) -> None:
        if self._on_state_changed:
            self._on_state_changed(event_type, data)
