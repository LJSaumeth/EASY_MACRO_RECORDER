from dataclasses import dataclass, field
from typing import List, Literal, Optional


EventType = Literal["mouse_click", "mouse_move", "key_press", "key_release"]
HotkeyAction = Literal["record_toggle", "playback_toggle", "emergency_stop"]


@dataclass
class MacroEvent:
    event_type: EventType
    timestamp: int
    button: Optional[str] = None
    key: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None


@dataclass
class RecordingSession:
    events: List[MacroEvent] = field(default_factory=list)
    start_time: Optional[float] = None
    is_recording: bool = False


@dataclass
class PlaybackSession:
    macro_events: List[MacroEvent] = field(default_factory=list)
    loop_count: int = 1
    current_loop: int = 0
    delay_between_loops: int = 0
    is_playing: bool = False
    current_event_index: int = 0


@dataclass
class Macro:
    name: str
    events: List[MacroEvent] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    INFINITE_LOOP = -1

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "events": [
                {
                    "event_type": e.event_type,
                    "timestamp": e.timestamp,
                    "button": e.button,
                    "key": e.key,
                    "x": e.x,
                    "y": e.y,
                }
                for e in self.events
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Macro":
        events = [
            MacroEvent(
                event_type=e["event_type"],
                timestamp=e["timestamp"],
                button=e.get("button"),
                key=e.get("key"),
                x=e.get("x"),
                y=e.get("y"),
            )
            for e in data.get("events", [])
        ]
        return cls(
            name=data.get("name", ""),
            events=events,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass
class HotkeyBinding:
    action: HotkeyAction
    key: str
    modifiers: List[str] = field(default_factory=list)


@dataclass
class HotkeyConfig:
    bindings: List[HotkeyBinding] = field(default_factory=list)

    @staticmethod
    def defaults() -> "HotkeyConfig":
        return HotkeyConfig(
            bindings=[
                HotkeyBinding(action="record_toggle", key="f6"),
                HotkeyBinding(action="playback_toggle", key="f7"),
                HotkeyBinding(action="emergency_stop", key="f8"),
            ]
        )

    def to_dict(self) -> dict:
        return {
            "bindings": [
                {"action": b.action, "key": b.key, "modifiers": b.modifiers}
                for b in self.bindings
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HotkeyConfig":
        bindings = [
            HotkeyBinding(
                action=b["action"],
                key=b["key"],
                modifiers=b.get("modifiers", []),
            )
            for b in data.get("bindings", [])
        ]
        return cls(bindings=bindings)
