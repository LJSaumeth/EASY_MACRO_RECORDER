"""Tests for HotkeyConfigStore — atomic writes (Fix)."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "macro_app"))

import tempfile
from domain.models import HotkeyConfig, HotkeyBinding
from infrastructure.hotkey_config_store import HotkeyConfigStore


class TestHotkeyConfigStore:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.store = HotkeyConfigStore(Path(self._tmpdir))

    def test_load_defaults_when_no_file(self):
        config = self.store.load_config()
        assert len(config.bindings) == 3
        actions = {b.action for b in config.bindings}
        assert "record_toggle" in actions

    def test_save_and_load(self):
        config = HotkeyConfig(bindings=[
            HotkeyBinding(action="record_toggle", key="f5"),
            HotkeyBinding(action="playback_toggle", key="f6"),
            HotkeyBinding(action="emergency_stop", key="f7"),
        ])
        self.store.save_config(config)
        loaded = self.store.load_config()
        assert len(loaded.bindings) == 3
        assert loaded.bindings[0].key == "f5"

    def test_atomic_write_creates_file(self):
        config = HotkeyConfig.defaults()
        self.store.save_config(config)
        path = Path(self._tmpdir) / ".hotkey_config.json"
        assert path.exists()
        assert path.is_file()

    def test_atomic_write_no_temp_files_left(self):
        config = HotkeyConfig.defaults()
        self.store.save_config(config)
        files = list(Path(self._tmpdir).iterdir())
        json_files = [f for f in files if f.suffix == ".json"]
        tmp_files = [f for f in files if ".json.tmp" in f.name]
        assert len(tmp_files) == 0, f"Temp files left behind: {tmp_files}"
        assert len(json_files) == 1

    def test_corrupted_file_returns_defaults(self):
        corrupted = Path(self._tmpdir) / ".hotkey_config.json"
        corrupted.write_text("NOT JSON", encoding="utf-8")
        config = self.store.load_config()
        assert len(config.bindings) == 3  # Falls back to defaults

    def test_overwrite_config(self):
        config1 = HotkeyConfig(bindings=[
            HotkeyBinding(action="record_toggle", key="f1"),
            HotkeyBinding(action="playback_toggle", key="f2"),
            HotkeyBinding(action="emergency_stop", key="f3"),
        ])
        config2 = HotkeyConfig(bindings=[
            HotkeyBinding(action="record_toggle", key="f9"),
            HotkeyBinding(action="playback_toggle", key="f10"),
            HotkeyBinding(action="emergency_stop", key="f11"),
        ])
        self.store.save_config(config1)
        self.store.save_config(config2)
        loaded = self.store.load_config()
        assert loaded.bindings[0].key == "f9"
