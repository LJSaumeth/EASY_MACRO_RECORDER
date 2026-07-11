"""Tests for PlaybackService — play, stop, loops, delay, set_macro_events."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "macro_app"))

import threading
from unittest.mock import MagicMock

from domain.models import Macro, MacroEvent
from application.playback_service import PlaybackService


def _make_playback(events=None):
    controller = MagicMock()
    playback = PlaybackService(controller)
    if events:
        playback.set_macro_events(events)
    return playback, controller


class TestPlaybackSetMacroEvents:
    """Fix #2: set_macro_events must persist changes."""

    def test_set_events(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback, _ = _make_playback()
        playback.set_macro_events(events)
        assert len(playback.get_current_macro()) == 1

    def test_set_events_replaces_existing(self):
        old = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        new = [
            MacroEvent(event_type="key_press", timestamp=0, key="x"),
            MacroEvent(event_type="key_press", timestamp=100, key="y"),
        ]
        playback, _ = _make_playback(old)
        playback.set_macro_events(new)
        assert len(playback.get_current_macro()) == 2
        assert playback.get_current_macro()[0].key == "x"

    def test_cannot_set_during_playback(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback, _ = _make_playback(events)
        playback._session.is_playing = True
        try:
            playback.set_macro_events([])
            assert False, "Should have raised RuntimeError"
        except RuntimeError:
            pass


class TestPlaybackLifecycle:
    def test_play_and_stop(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=10000, key="b"),
        ]
        playback, _ = _make_playback(events)

        result = playback.play(loop_count=1)
        assert result["success"] is True
        assert playback.is_playing() is True

        time.sleep(0.05)
        result = playback.stop()
        assert result["success"] is True
        assert playback.is_playing() is False

    def test_play_empty_macro_fails(self):
        playback, _ = _make_playback()
        result = playback.play()
        assert result["success"] is False
        assert "No macro loaded" in result["error"]

    def test_stop_when_not_playing_fails(self):
        playback, _ = _make_playback()
        result = playback.stop()
        assert result["success"] is False
        assert "Not playing" in result["error"]

    def test_play_already_playing_fails(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="a"),
            MacroEvent(event_type="key_press", timestamp=10000, key="b"),
        ]
        playback, _ = _make_playback(events)
        playback.play(loop_count=Macro.INFINITE_LOOP)
        time.sleep(0.05)
        result = playback.play(loop_count=1)
        assert result["success"] is False
        assert "Already playing" in result["error"]
        playback.stop()

    def test_get_state(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback, _ = _make_playback(events)
        state = playback.get_state()
        assert state["is_playing"] is False
        assert state["total_events"] == 1
        assert state["loop_count"] == 1


class TestPlaybackInfiniteLoop:
    def test_infinite_loop_constant(self):
        assert Macro.INFINITE_LOOP == -1

    def test_play_with_infinite_loop(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback, _ = _make_playback(events)
        result = playback.play(loop_count=Macro.INFINITE_LOOP)
        assert result["success"] is True
        time.sleep(0.2)
        assert playback.is_playing() is True
        playback.stop()
        assert playback.is_playing() is False


class TestPlaybackThreadSafety:
    def test_concurrent_stop(self):
        """Multiple threads calling stop should not crash."""
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        playback, _ = _make_playback(events)
        playback.play(loop_count=Macro.INFINITE_LOOP)

        errors = []
        def try_stop():
            try:
                playback.stop()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=try_stop) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Only one should succeed, rest should get "Not playing"
        assert len(errors) == 0  # No crashes
        assert playback.is_playing() is False
