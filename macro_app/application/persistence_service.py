from datetime import datetime, timezone
from typing import List

from domain.exceptions import InvalidMacroNameError, MacroNotFoundError
from domain.models import Macro, MacroEvent
from infrastructure.json_file_storage import JsonFileStorage


class PersistenceService:
    def __init__(self, storage: JsonFileStorage):
        self._storage = storage

    def save_macro(self, name: str, events: List[MacroEvent]) -> Macro:
        if not name or not name.strip():
            raise InvalidMacroNameError("Macro name cannot be empty")
        sanitized = self._storage.sanitize_name(name)
        if not sanitized:
            raise InvalidMacroNameError("Macro name contains no valid characters")
        now = datetime.now(timezone.utc).isoformat()
        try:
            existing = self._storage.load(sanitized)
            macro = Macro(
                name=sanitized,
                events=list(events),
                created_at=existing.created_at,
                updated_at=now,
            )
        except MacroNotFoundError:
            macro = Macro(
                name=sanitized,
                events=list(events),
                created_at=now,
                updated_at=now,
            )
        self._storage.save(macro)
        return macro

    def load_macro(self, name: str) -> Macro:
        sanitized = self._storage.sanitize_name(name)
        return self._storage.load(sanitized)

    def list_macros(self) -> List[str]:
        return self._storage.list_all()

    def delete_macro(self, name: str) -> None:
        sanitized = self._storage.sanitize_name(name)
        self._storage.delete(sanitized)
