"""Tests for MacroApi — integration tests for the JS bridge layer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "macro_app"))

import tempfile
import threading
import time
from unittest.mock import MagicMock

from domain.models import MacroEvent
from application.recording_service import RecordingService
from application.playback_service import PlaybackService
from application.persistence_service import PersistenceService
from application.hotkey_service import HotkeyService
from application.macro_editor import MacroEditor
from presentation.api import MacroApi
from infrastructure.json_file_storage import JsonFileStorage


def _make_api():
    """Build a MacroApi with all dependencies mocked (no pynput)."""
    tmpdir = tempfile.mkdtemp()
    file_storage = JsonFileStorage(Path(tmpdir) / "macros")

    listener = MagicMock()
    controller = MagicMock()
    hotkey_listener = MagicMock()
    config_store = MagicMock()
    config_store.load_config.return_value = MagicMock(bindings=[])

    recording = RecordingService(listener)
    playback = PlaybackService(controller)
    persistence = PersistenceService(file_storage)
    hotkey = MagicMock(spec=HotkeyService)
    hotkey.get_bindings.return_value = []
    editor = MacroEditor(recording, playback)

    api = MacroApi(
        recording_service=recording,
        playback_service=playback,
        persistence_service=persistence,
        hotkey_service=hotkey,
        macro_editor=editor,
    )
    return api, recording, playback


class TestApiRecording:
    def test_start_stop_recording(self):
        api, recording, _ = _make_api()
        result = api.start_recording()
        assert result["success"] is True
        assert api._recording.is_recording() is True

        result = api.stop_recording()
        assert result["success"] is True
        assert api._recording.is_recording() is False


class TestApiState:
    def test_get_app_state_structure(self):
        api, _, _ = _make_api()
        state = api.get_app_state()
        assert "is_recording" in state
        assert "is_playing" in state
        assert "playback" in state
        assert "can_edit" in state
        assert "events" in state

    def test_pending_events_drained(self):
        api, _, _ = _make_api()
        api._on_state_event("test_event", {"key": "value"})
        api._on_state_event("another", {})

        state = api.get_app_state()
        assert len(state["events"]) == 2
        assert state["events"][0]["type"] == "test_event"
        assert state["events"][1]["type"] == "another"

        # Second call should be empty
        state2 = api.get_app_state()
        assert len(state2["events"]) == 0


class TestApiThreadSafety:
    """Fix #1: _pending_events must be thread-safe."""

    def test_concurrent_event_appending(self):
        api, _, _ = _make_api()
        num_threads = 10
        events_per_thread = 100

        def append_events():
            for _ in range(events_per_thread):
                api._on_state_event("test", {})

        threads = [threading.Thread(target=append_events) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        state = api.get_app_state()
        expected = num_threads * events_per_thread
        assert len(state["events"]) == expected, f"Expected {expected}, got {len(state['events'])}"

    def test_concurrent_read_write(self):
        api, _, _ = _make_api()
        errors = []

        def writer():
            for _ in range(200):
                api._on_state_event("w", {})

        def reader():
            for _ in range(200):
                try:
                    api.get_app_state()
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=writer),
            threading.Thread(target=reader),
            threading.Thread(target=reader),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"


class TestApiMacroEvents:
    def test_get_macro_events_empty(self):
        api, _, _ = _make_api()
        result = api.get_macro_events()
        assert result["success"] is True
        assert result["events"] == []

    def test_get_macro_events_after_set(self):
        api, _, playback = _make_api()
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_release", timestamp=100, key="a"),
        ]
        playback.set_macro_events(events)

        result = api.get_macro_events()
        assert result["success"] is True
        assert len(result["events"]) == 2
        assert result["events"][0]["key"] == "a"
        assert result["events"][1]["timestamp"] == 100


class TestApiMacroEditor:
    def test_delete_event(self):
        api, _, playback = _make_api()
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
        ]
        playback.set_macro_events(events)

        result = api.delete_macro_event(0)
        assert result["success"] is True
        assert len(playback.get_current_macro()) == 1

    def test_adjust_timestamp(self):
        api, _, playback = _make_api()
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
        ]
        playback.set_macro_events(events)

        result = api.adjust_event_timestamp(0, 50)
        assert result["success"] is True
        assert playback.get_current_macro()[0].timestamp == 50
        assert playback.get_current_macro()[1].timestamp == 150

    def test_insert_event(self):
        api, _, playback = _make_api()
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback.set_macro_events(events)

        result = api.insert_macro_event(1, "key_press", 0, "", "b", 0, 0)
        assert result["success"] is True
        assert len(playback.get_current_macro()) == 2

    def test_insert_delay(self):
        api, _, playback = _make_api()
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
        ]
        playback.set_macro_events(events)

        result = api.insert_macro_delay(1, 500)
        assert result["success"] is True
        assert playback.get_current_macro()[1].timestamp == 600

    def test_clear_events(self):
        api, _, playback = _make_api()
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback.set_macro_events(events)

        result = api.clear_macro_events()
        assert result["success"] is True
        assert len(playback.get_current_macro()) == 0

    def test_can_edit_macro(self):
        api, _, _ = _make_api()
        result = api.can_edit_macro()
        assert result["success"] is True
        assert result["can_edit"] is True
