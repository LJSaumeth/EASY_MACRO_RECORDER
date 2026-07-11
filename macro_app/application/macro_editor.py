from typing import List

from domain.exceptions import EditingNotAllowedError
from domain.models import MacroEvent
from application.recording_service import RecordingService
from application.playback_service import PlaybackService


class MacroEditor:
    def __init__(
        self,
        recording_service: RecordingService,
        playback_service: PlaybackService,
    ):
        self._recording = recording_service
        self._playback = playback_service

    def can_edit(self) -> bool:
        return not self._recording.is_recording() and not self._playback.is_playing()

    def _guard(self) -> None:
        if not self.can_edit():
            raise EditingNotAllowedError("Cannot edit while recording or playing back")

    def get_events(self) -> List[MacroEvent]:
        self._guard()
        return self._playback.get_current_macro()

    def delete_event(self, index: int) -> List[MacroEvent]:
        self._guard()
        events = self._playback.get_current_macro()
        if index < 0 or index >= len(events):
            raise IndexError(f"Event index {index} out of range (0-{len(events) - 1})")
        del events[index]
        return events

    def adjust_timestamp(self, index: int, delta_ms: int) -> List[MacroEvent]:
        self._guard()
        events = self._playback.get_current_macro()
        if index < 0 or index >= len(events):
            raise IndexError(f"Event index {index} out of range (0-{len(events) - 1})")
        effective_delta = delta_ms
        if events[index].timestamp + delta_ms < 0:
            effective_delta = -events[index].timestamp
        events[index].timestamp += effective_delta
        for i in range(index + 1, len(events)):
            events[i].timestamp += effective_delta
        return events

    def insert_event(self, index: int, event: MacroEvent) -> List[MacroEvent]:
        self._guard()
        events = self._playback.get_current_macro()
        if index < 0 or index > len(events):
            raise IndexError(f"Event index {index} out of range (0-{len(events)})")
        if index == len(events):
            previous_timestamp = events[-1].timestamp if events else 0
            event.timestamp = previous_timestamp + 100
            events.append(event)
        else:
            base_timestamp = events[index].timestamp
            event.timestamp = base_timestamp
            events.insert(index, event)
        return events

    def insert_delay(self, index: int, duration_ms: int) -> List[MacroEvent]:
        self._guard()
        if duration_ms <= 0:
            raise ValueError("Delay duration must be positive")
        self._guard()
        events = self._playback.get_current_macro()
        if index < 0 or index > len(events):
            raise IndexError(f"Event index {index} out of range (0-{len(events)})")
        if index == len(events):
            return events
        for i in range(index, len(events)):
            events[i].timestamp += duration_ms
        return events

    def clear_all_events(self) -> List[MacroEvent]:
        self._guard()
        events = self._playback.get_current_macro()
        events.clear()
        return events
