import time
from typing import Callable, Dict, List, Optional

from pynput import keyboard, mouse

from domain.models import MacroEvent, HotkeyBinding


class PynputListener:
    def __init__(self):
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._event_callback: Optional[Callable[[MacroEvent], None]] = None
        self._start_time: Optional[float] = None
        self._is_listening: bool = False

    def start_listening(self, callback: Callable[[MacroEvent], None]) -> None:
        if self._is_listening:
            return
        self._event_callback = callback
        self._start_time = time.time()
        self._is_listening = True
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop_listening(self) -> None:
        if not self._is_listening:
            return
        self._is_listening = False
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        self._event_callback = None
        self._start_time = None

    def is_listening(self) -> bool:
        return self._is_listening

    def _relative_timestamp(self) -> int:
        if self._start_time is None:
            return 0
        return int((time.time() - self._start_time) * 1000)

    def _emit_event(self, event: MacroEvent) -> None:
        if self._event_callback:
            self._event_callback(event)

    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> bool:
        if not self._is_listening:
            return True
        button_name = button.name
        event = MacroEvent(
            event_type="mouse_click",
            timestamp=self._relative_timestamp(),
            button=button_name,
            x=x,
            y=y,
        )
        self._emit_event(event)
        return True

    def _on_mouse_move(self, x: int, y: int) -> bool:
        if not self._is_listening:
            return True
        event = MacroEvent(
            event_type="mouse_move",
            timestamp=self._relative_timestamp(),
            x=x,
            y=y,
        )
        self._emit_event(event)
        return True

    def _on_key_press(self, key) -> bool:
        if not self._is_listening:
            return True
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).replace("Key.", "")
        event = MacroEvent(
            event_type="key_press",
            timestamp=self._relative_timestamp(),
            key=key_name,
        )
        self._emit_event(event)
        return True

    def _on_key_release(self, key) -> bool:
        if not self._is_listening:
            return True
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).replace("Key.", "")
        event = MacroEvent(
            event_type="key_release",
            timestamp=self._relative_timestamp(),
            key=key_name,
        )
        self._emit_event(event)
        return True


OS_RESERVED_KEYS = {
    ("alt", "f4"),
    ("ctrl", "alt", "del"),
    ("cmd", "q"),
    ("win", "l"),
}


class GlobalHotkeyListener:
    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._bindings: Dict[str, HotkeyBinding] = {}
        self._callbacks: Dict[str, Callable[[], None]] = {}
        self._is_running: bool = False

    def start(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()

    def stop(self) -> None:
        self._is_running = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    def is_running(self) -> bool:
        return self._is_running

    def register_hotkey(self, binding: HotkeyBinding, callback: Callable[[], None]) -> None:
        key_name = self._normalize_key(binding.key, binding.modifiers)
        self._bindings[key_name] = binding
        self._callbacks[key_name] = callback

    def unregister_hotkey(self, binding: HotkeyBinding) -> None:
        key_name = self._normalize_key(binding.key, binding.modifiers)
        self._bindings.pop(key_name, None)
        self._callbacks.pop(key_name, None)

    def clear_all(self) -> None:
        self._bindings.clear()
        self._callbacks.clear()

    def _on_press(self, key) -> bool:
        try:
            key_name = key.char if hasattr(key, "char") else str(key).replace("Key.", "")
        except AttributeError:
            key_name = str(key).replace("Key.", "")
        key_name = key_name.lower()
        if key_name in self._callbacks:
            self._callbacks[key_name]()
        return True

    @staticmethod
    def _normalize_key(key: str, modifiers: List[str]) -> str:
        if not modifiers:
            return key.lower()
        parts = sorted(modifiers) + [key.lower()]
        return "+".join(parts)

    @staticmethod
    def is_os_reserved(key: str, modifiers: List[str]) -> bool:
        combo = tuple(sorted(modifiers) + [key.lower()])
        return combo in OS_RESERVED_KEYS
