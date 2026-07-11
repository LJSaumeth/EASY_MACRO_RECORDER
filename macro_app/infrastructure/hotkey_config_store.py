from pathlib import Path

from domain.models import HotkeyConfig


HOTKEY_CONFIG_FILENAME = ".hotkey_config.json"


class HotkeyConfigStore:
    def __init__(self, storage_path: Path):
        self._config_path = storage_path / HOTKEY_CONFIG_FILENAME

    def load_config(self) -> HotkeyConfig:
        if not self._config_path.exists():
            return HotkeyConfig.defaults()
        import json

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return HotkeyConfig.from_dict(data)
        except (json.JSONDecodeError, OSError, KeyError):
            return HotkeyConfig.defaults()

    def save_config(self, config: HotkeyConfig) -> None:
        import json

        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        json_text = json.dumps(config.to_dict(), indent=2, ensure_ascii=False)
        with open(self._config_path, "w", encoding="utf-8") as f:
            f.write(json_text)
