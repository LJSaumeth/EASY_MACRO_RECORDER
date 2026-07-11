import json
import os
import tempfile
from pathlib import Path

from domain.models import HotkeyConfig


HOTKEY_CONFIG_FILENAME = ".hotkey_config.json"


class HotkeyConfigStore:
    def __init__(self, storage_path: Path):
        self._config_path = storage_path / HOTKEY_CONFIG_FILENAME

    def load_config(self) -> HotkeyConfig:
        if not self._config_path.exists():
            return HotkeyConfig.defaults()

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return HotkeyConfig.from_dict(data)
        except (json.JSONDecodeError, OSError, KeyError):
            return HotkeyConfig.defaults()

    def save_config(self, config: HotkeyConfig) -> None:
        """Atomically write hotkey config using temp file + rename."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        json_text = json.dumps(config.to_dict(), indent=2, ensure_ascii=False)

        temp_fd, temp_path = tempfile.mkstemp(
            dir=str(self._config_path.parent),
            suffix=".json.tmp",
        )
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(json_text)
            os.replace(temp_path, str(self._config_path))
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
