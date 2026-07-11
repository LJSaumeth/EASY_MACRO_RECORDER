"""Tests for domain models: MacroEvent, Macro, HotkeyConfig."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "macro_app"))

from domain.models import Macro, MacroEvent, HotkeyBinding, HotkeyConfig


# ── MacroEvent ─────────────────────────────────────────────────────
class TestMacroEvent:
    def test_create_key_press(self):
        e = MacroEvent(event_type="key_press", timestamp=100, key="a")
        assert e.event_type == "key_press"
        assert e.timestamp == 100
        assert e.key == "a"
        assert e.button is None
        assert e.x is None

    def test_create_mouse_click(self):
        e = MacroEvent(event_type="mouse_click", timestamp=0, button="left", x=100, y=200)
        assert e.button == "left"
        assert e.x == 100
        assert e.y == 200

    def test_create_mouse_move(self):
        e = MacroEvent(event_type="mouse_move", timestamp=50, x=500, y=600)
        assert e.x == 500
        assert e.y == 600
        assert e.key is None


# ── Macro ──────────────────────────────────────────────────────────
class TestMacro:
    def test_infinite_loop_sentinel(self):
        assert Macro.INFINITE_LOOP == -1

    def test_to_dict_roundtrip(self):
        events = [
            MacroEvent(event_type="key_press", timestamp=0, key="w"),
            MacroEvent(event_type="key_release", timestamp=100, key="w"),
            MacroEvent(event_type="mouse_click", timestamp=200, button="left", x=10, y=20),
        ]
        macro = Macro(name="test", events=events, created_at="2026-01-01", updated_at="2026-01-02")
        d = macro.to_dict()
        restored = Macro.from_dict(d)
        assert restored.name == "test"
        assert len(restored.events) == 3
        assert restored.events[0].key == "w"
        assert restored.events[2].button == "left"
        assert restored.created_at == "2026-01-01"

    def test_from_dict_defaults(self):
        m = Macro.from_dict({})
        assert m.name == ""
        assert m.events == []
        assert m.created_at == ""

    def test_from_dict_missing_events(self):
        m = Macro.from_dict({"name": "x"})
        assert m.events == []


# ── HotkeyConfig ───────────────────────────────────────────────────
class TestHotkeyConfig:
    def test_defaults(self):
        cfg = HotkeyConfig.defaults()
        assert len(cfg.bindings) == 3
        actions = {b.action for b in cfg.bindings}
        assert actions == {"record_toggle", "playback_toggle", "emergency_stop"}

    def test_to_dict_roundtrip(self):
        cfg = HotkeyConfig.defaults()
        d = cfg.to_dict()
        restored = HotkeyConfig.from_dict(d)
        assert len(restored.bindings) == 3
        for orig, back in zip(cfg.bindings, restored.bindings):
            assert orig.action == back.action
            assert orig.key == back.key
            assert orig.modifiers == back.modifiers

    def test_from_dict_empty(self):
        cfg = HotkeyConfig.from_dict({})
        assert cfg.bindings == []

    def test_from_dict_with_modifiers(self):
        data = {"bindings": [{"action": "record_toggle", "key": "f6", "modifiers": ["ctrl"]}]}
        cfg = HotkeyConfig.from_dict(data)
        assert cfg.bindings[0].modifiers == ["ctrl"]
