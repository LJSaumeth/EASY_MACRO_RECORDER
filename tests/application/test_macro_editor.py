"""Tests for MacroEditor — verifies that mutations persist (Fix #2)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "macro_app"))

import threading
from unittest.mock import MagicMock

from domain.models import MacroEvent
from application.playback_service import PlaybackService
from application.recording_service import RecordingService
from application.macro_editor import MacroEditor
from domain.exceptions import EditingNotAllowedError


def _make_editor(events=None):
    """Build a MacroEditor with mocked recording/playback services."""
    controller = MagicMock()
    playback = PlaybackService(controller)
    recording = MagicMock(spec=RecordingService)
    recording.is_recording.return_value = False

    if events:
        playback.set_macro_events(events)

    editor = MacroEditor(recording, playback)
    return editor, playback, recording


class TestMacroEditorDeletePersists:
    """Fix #2: delete_event must persist changes to PlaybackService."""

    def test_delete_persists_in_playback(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_release", timestamp=100, key="a"),
            MacroEvent(event_type="key_press", timestamp=200, key="b"),
        ]
        editor, playback, _ = _make_editor(events)

        editor.delete_event(1)  # Delete middle event

        remaining = playback.get_current_macro()
        assert len(remaining) == 2
        assert remaining[0].key == "a"
        assert remaining[1].key == "b"

    def test_delete_first_event(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="x"),
            MacroEvent(event_type="key_press", timestamp=100, key="y"),
        ]
        editor, playback, _ = _make_editor(events)
        editor.delete_event(0)
        assert len(playback.get_current_macro()) == 1
        assert playback.get_current_macro()[0].key == "y"

    def test_delete_last_event(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="x"),
            MacroEvent(event_type="key_press", timestamp=100, key="y"),
        ]
        editor, playback, _ = _make_editor(events)
        editor.delete_event(1)
        assert len(playback.get_current_macro()) == 1
        assert playback.get_current_macro()[0].key == "x"

    def test_delete_out_of_range_raises(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        editor, _, _ = _make_editor(events)
        try:
            editor.delete_event(5)
            assert False, "Should have raised IndexError"
        except IndexError:
            pass


class TestMacroEditorAdjustTimestamp:
    def test_adjust_shifts_subsequent_events(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
            MacroEvent(event_type="key_press", timestamp=200, key="c"),
        ]
        editor, playback, _ = _make_editor(events)
        editor.adjust_timestamp(0, 50)

        result = playback.get_current_macro()
        assert result[0].timestamp == 50
        assert result[1].timestamp == 150
        assert result[2].timestamp == 250

    def test_adjust_cannot_go_negative(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=10, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
        ]
        editor, playback, _ = _make_editor(events)
        editor.adjust_timestamp(0, -200)  # Would go to -190

        result = playback.get_current_macro()
        assert result[0].timestamp == 0  # Clamped to 0
        assert result[1].timestamp == 90  # Shifted by -10


class TestMacroEditorInsertEvent:
    def test_insert_at_end(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        editor, playback, _ = _make_editor(events)
        new_event = MacroEvent(event_type="key_press", timestamp=0, key="b")
        editor.insert_event(1, new_event)

        result = playback.get_current_macro()
        assert len(result) == 2
        assert result[1].key == "b"

    def test_insert_in_middle(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=200, key="c"),
        ]
        editor, playback, _ = _make_editor(events)
        new_event = MacroEvent(event_type="key_press", timestamp=0, key="b")
        editor.insert_event(1, new_event)

        result = playback.get_current_macro()
        assert len(result) == 3
        assert result[0].key == "a"
        assert result[1].key == "b"
        assert result[2].key == "c"


class TestMacroEditorInsertDelay:
    def test_insert_delay_shifts_events(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
        ]
        editor, playback, _ = _make_editor(events)
        editor.insert_delay(1, 500)

        result = playback.get_current_macro()
        assert result[0].timestamp == 0
        assert result[1].timestamp == 600  # 100 + 500

    def test_insert_delay_negative_raises(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        editor, _, _ = _make_editor(events)
        try:
            editor.insert_delay(0, -100)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestMacroEditorClearAll:
    def test_clear_all(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=100, key="b"),
        ]
        editor, playback, _ = _make_editor(events)
        editor.clear_all_events()
        assert len(playback.get_current_macro()) == 0


class TestMacroEditorGuard:
    def test_cannot_edit_while_recording(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        editor, playback, recording = _make_editor(events)
        recording.is_recording.return_value = True

        try:
            editor.get_events()
            assert False, "Should have raised EditingNotAllowedError"
        except EditingNotAllowedError:
            pass

    def test_cannot_edit_while_playing(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        editor, playback, recording = _make_editor(events)
        playback._session.is_playing = True

        try:
            editor.delete_event(0)
            assert False, "Should have raised EditingNotAllowedError"
        except EditingNotAllowedError:
            pass
