"""Tests for JsonFileStorage — atomic writes, corruption handling."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "macro_app"))

import tempfile
from domain.models import Macro, MacroEvent
from infrastructure.json_file_storage import JsonFileStorage
from domain.exceptions import MacroNotFoundError, CorruptedMacroError


class TestJsonFileStorage:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.storage = JsonFileStorage(Path(self._tmpdir))

    def test_save_and_load(self):
        events = [MacroEvent(event_type="key_press", timestamp=0, key="a")]
        macro = Macro(name="test-macro", events=events)
        self.storage.save(macro)

        loaded = self.storage.load("test-macro")
        assert loaded.name == "test-macro"
        assert len(loaded.events) == 1
        assert loaded.events[0].key == "a"

    def test_list_all(self):
        for name in ["alpha", "beta", "gamma"]:
            macro = Macro(name=name, events=[])
            self.storage.save(macro)

        names = self.storage.list_all()
        assert names == ["alpha", "beta", "gamma"]

    def test_delete(self):
        macro = Macro(name="to-delete", events=[])
        self.storage.save(macro)
        self.storage.delete("to-delete")
        try:
            self.storage.load("to-delete")
            assert False, "Should have raised MacroNotFoundError"
        except MacroNotFoundError:
            pass

    def test_delete_nonexistent_raises(self):
        try:
            self.storage.delete("does-not-exist")
            assert False, "Should have raised MacroNotFoundError"
        except MacroNotFoundError:
            pass

    def test_load_nonexistent_raises(self):
        try:
            self.storage.load("ghost")
            assert False, "Should have raised MacroNotFoundError"
        except MacroNotFoundError:
            pass

    def test_load_corrupted_file(self):
        corrupted = Path(self._tmpdir) / "broken.json"
        corrupted.write_text("NOT VALID JSON {{{", encoding="utf-8")
        try:
            self.storage.load("broken")
            assert False, "Should have raised CorruptedMacroError"
        except CorruptedMacroError:
            pass

    def test_load_invalid_structure(self):
        bad = Path(self._tmpdir) / "bad.json"
        bad.write_text(json.dumps({"name": "bad", "not_events": True}), encoding="utf-8")
        try:
            self.storage.load("bad")
            assert False, "Should have raised CorruptedMacroError"
        except CorruptedMacroError:
            pass

    def test_sanitize_name(self):
        assert JsonFileStorage.sanitize_name("hello world") == "helloworld"
        assert JsonFileStorage.sanitize_name("test-macro_123") == "test-macro_123"
        import pytest
        with pytest.raises(ValueError):
            JsonFileStorage.sanitize_name("!!!@@@###")

    def test_overwrite_existing(self):
        macro1 = Macro(name="overwrite", events=[MacroEvent(event_type="key_press", timestamp=0, key="a")])
        macro2 = Macro(name="overwrite", events=[MacroEvent(event_type="key_press", timestamp=0, key="z")])
        self.storage.save(macro1)
        self.storage.save(macro2)
        loaded = self.storage.load("overwrite")
        assert loaded.events[0].key == "z"

    def test_atomic_write(self):
        """Verify file exists after save (atomic write succeeded)."""
        macro = Macro(name="atomic", events=[])
        self.storage.save(macro)
        path = Path(self._tmpdir) / "atomic.json"
        assert path.exists()
        assert path.is_file()
