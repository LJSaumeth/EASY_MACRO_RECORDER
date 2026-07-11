from pynput import keyboard as kb
from pynput import mouse as ms

from domain.models import MacroEvent


class PynputController:
    def __init__(self):
        self._mouse = ms.Controller()
        self._keyboard = kb.Controller()

    def execute_event(self, event: MacroEvent) -> None:
        if event.event_type == "mouse_click":
            self._mouse_click(event)
        elif event.event_type == "mouse_move":
            self._mouse_move(event)
        elif event.event_type == "key_press":
            self._key_action(event, is_press=True)
        elif event.event_type == "key_release":
            self._key_action(event, is_press=False)

    def _mouse_click(self, event: MacroEvent) -> None:
        if event.x is not None and event.y is not None:
            self._mouse.position = (event.x, event.y)
        button = self._resolve_button(event.button)
        self._mouse.click(button)

    def _mouse_move(self, event: MacroEvent) -> None:
        if event.x is not None and event.y is not None:
            self._mouse.position = (event.x, event.y)

    def _key_action(self, event: MacroEvent, is_press: bool) -> None:
        if event.key is None:
            return
        resolved_key = self._resolve_key(event.key)
        # Skip unsupported keys (e.g. multimedia) instead of crashing
        if isinstance(resolved_key, str):
            return
        try:
            if is_press:
                self._keyboard.press(resolved_key)
            else:
                self._keyboard.release(resolved_key)
        except Exception:
            pass  # Key not supported by current platform, skip silently

    @staticmethod
    def _resolve_button(button_name: str) -> ms.Button:
        button_map = {
            "left": ms.Button.left,
            "right": ms.Button.right,
            "middle": ms.Button.middle,
        }
        return button_map.get(button_name, ms.Button.left)

    @staticmethod
    def _resolve_key(key_name: str):
        special_keys = {
            "space": kb.Key.space,
            "enter": kb.Key.enter,
            "tab": kb.Key.tab,
            "esc": kb.Key.esc,
            "escape": kb.Key.esc,
            "backspace": kb.Key.backspace,
            "delete": kb.Key.delete,
            "shift": kb.Key.shift,
            "shift_l": kb.Key.shift_l,
            "shift_r": kb.Key.shift_r,
            "ctrl": kb.Key.ctrl,
            "ctrl_l": kb.Key.ctrl_l,
            "ctrl_r": kb.Key.ctrl_r,
            "alt": kb.Key.alt,
            "alt_l": kb.Key.alt_l,
            "alt_r": kb.Key.alt_r,
            "up": kb.Key.up,
            "down": kb.Key.down,
            "left": kb.Key.left,
            "right": kb.Key.right,
            "f1": kb.Key.f1,
            "f2": kb.Key.f2,
            "f3": kb.Key.f3,
            "f4": kb.Key.f4,
            "f5": kb.Key.f5,
            "f6": kb.Key.f6,
            "f7": kb.Key.f7,
            "f8": kb.Key.f8,
            "f9": kb.Key.f9,
            "f10": kb.Key.f10,
            "f11": kb.Key.f11,
            "f12": kb.Key.f12,
            "caps_lock": kb.Key.caps_lock,
            "num_lock": kb.Key.num_lock,
            "page_up": kb.Key.page_up,
            "page_down": kb.Key.page_down,
            "home": kb.Key.home,
            "end": kb.Key.end,
            "insert": kb.Key.insert,
            "print_screen": kb.Key.print_screen,
            "cmd": kb.Key.cmd,
            "cmd_l": kb.Key.cmd_l,
            "cmd_r": kb.Key.cmd_r,
        }
        if key_name in special_keys:
            return special_keys[key_name]
        if len(key_name) == 1:
            return kb.KeyCode.from_char(key_name)
        return kb.KeyCode.from_char(key_name) if len(key_name) == 1 else key_name
