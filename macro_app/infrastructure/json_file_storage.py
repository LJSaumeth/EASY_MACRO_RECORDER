import json
import os
import re
import tempfile
from pathlib import Path
from typing import List

from domain.exceptions import CorruptedMacroError, MacroNotFoundError
from domain.models import Macro


class JsonFileStorage:
    def __init__(self, storage_path: Path):
        self._storage_path = storage_path
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def save(self, macro: Macro) -> None:
        file_path = self._filename_for(macro.name)
        data = macro.to_dict()
        json_text = json.dumps(data, indent=2, ensure_ascii=False)
        temp_fd, temp_path = tempfile.mkstemp(dir=str(self._storage_path), suffix=".json")
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(json_text)
            os.replace(temp_path, str(file_path))
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def load(self, name: str) -> Macro:
        file_path = self._filename_for(name)
        if not file_path.exists():
            raise MacroNotFoundError(f"Macro '{name}' not found")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            raise CorruptedMacroError(f"Macro file '{name}' is corrupted")
        if "events" not in data or not isinstance(data["events"], list):
            raise CorruptedMacroError(f"Macro file '{name}' has an invalid structure")
        data["name"] = name
        return Macro.from_dict(data)

    def list_all(self) -> List[str]:
        if not self._storage_path.exists():
            return []
        names = []
        for entry in self._storage_path.iterdir():
            if entry.is_file() and entry.suffix == ".json":
                names.append(entry.stem)
        return sorted(names)

    def delete(self, name: str) -> None:
        file_path = self._filename_for(name)
        if not file_path.exists():
            raise MacroNotFoundError(f"Macro '{name}' not found")
        file_path.unlink()

    @staticmethod
    def sanitize_name(name: str) -> str:
        sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "", name)
        if not sanitized:
            raise ValueError("Macro name contains no valid characters")
        return sanitized

    def _filename_for(self, name: str) -> Path:
        sanitized = self.sanitize_name(name)
        return self._storage_path / f"{sanitized}.json"
