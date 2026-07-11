import threading
import time
from typing import Callable, List, Optional

from domain.models import MacroEvent, PlaybackSession
from infrastructure.pynput_controller import PynputController


class PlaybackService:
    def __init__(self, controller: PynputController):
        self._controller = controller
        self._session = PlaybackSession()
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._on_state_changed: Optional[Callable[[str, dict], None]] = None

    def set_state_callback(self, callback: Callable[[str, dict], None]) -> None:
        self._on_state_changed = callback

    def set_macro(self, events: List[MacroEvent]) -> dict:
        if self._session.is_playing:
            return {"success": False, "error": "Cannot change macro during playback"}
        self._session.macro_events = list(events)
        return {"success": True, "event_count": len(events)}

    def play(self, loop_count: int = 1, delay_between_loops: int = 0) -> dict:
        if self._session.is_playing:
            return {"success": False, "error": "Already playing"}
        if not self._session.macro_events:
            return {"success": False, "error": "No macro loaded"}
        self._session = PlaybackSession(
            macro_events=list(self._session.macro_events),
            loop_count=loop_count,
            current_loop=0,
            delay_between_loops=delay_between_loops,
            is_playing=True,
            current_event_index=0,
        )
        self._stop_event.clear()
        self._playback_thread = threading.Thread(target=self._run_playback, daemon=True)
        self._playback_thread.start()
        self._notify("playback_started", {})
        return {"success": True}

    def stop(self) -> dict:
        if not self._session.is_playing:
            return {"success": False, "error": "Not playing"}
        self._stop_event.set()
        self._session.is_playing = False
        self._notify("playback_stopped", {})
        return {"success": True}

    def is_playing(self) -> bool:
        return self._session.is_playing

    def get_state(self) -> dict:
        return {
            "is_playing": self._session.is_playing,
            "current_loop": self._session.current_loop,
            "loop_count": self._session.loop_count,
            "current_event_index": self._session.current_event_index,
            "total_events": len(self._session.macro_events),
        }

    def get_current_macro(self) -> List[MacroEvent]:
        return list(self._session.macro_events)

    def _run_playback(self) -> None:
        max_loops = self._session.loop_count
        is_infinite = max_loops == -1
        while self._session.is_playing and not self._stop_event.is_set():
            if not is_infinite and self._session.current_loop >= max_loops:
                break
            self._execute_single_loop()
            self._session.current_loop += 1
            if self._session.is_playing and not self._stop_event.is_set():
                self._wait_for_delay(self._session.delay_between_loops)
        self._session.is_playing = False
        self._notify("playback_completed", {})

    def _execute_single_loop(self) -> None:
        events = self._session.macro_events
        previous_timestamp = events[0].timestamp if events else 0
        for index, event in enumerate(events):
            if self._stop_event.is_set() or not self._session.is_playing:
                return
            self._session.current_event_index = index
            delta = event.timestamp - previous_timestamp
            if delta > 0:
                self._wait_for_delay(delta)
            if self._stop_event.is_set() or not self._session.is_playing:
                return
            self._controller.execute_event(event)
            previous_timestamp = event.timestamp

    def _wait_for_delay(self, delay_ms: int) -> None:
        if delay_ms <= 0:
            return
        step = 0.05
        elapsed = 0.0
        while elapsed < delay_ms / 1000.0:
            if self._stop_event.is_set():
                return
            time.sleep(step)
            elapsed += step

    def _notify(self, event_type: str, data: dict) -> None:
        if self._on_state_changed:
            self._on_state_changed(event_type, data)
