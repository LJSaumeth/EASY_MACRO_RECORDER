import getpass
import os
import sys
from pathlib import Path

import webview

from infrastructure.pynput_listener import PynputListener, GlobalHotkeyListener
from infrastructure.pynput_controller import PynputController
from infrastructure.json_file_storage import JsonFileStorage
from infrastructure.hotkey_config_store import HotkeyConfigStore
from application.recording_service import RecordingService
from application.playback_service import PlaybackService
from application.persistence_service import PersistenceService
from application.hotkey_service import HotkeyService
from application.macro_editor import MacroEditor
from presentation.api import MacroApi


def _get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(os.path.dirname(os.path.abspath(__file__)))


def _get_frontend_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "frontend"
    return Path(os.path.dirname(os.path.abspath(__file__))) / "frontend"


MACROS_DIR = _get_app_dir() / "macros"
FRONTEND_DIR = _get_frontend_dir()


def build_services():
    listener = PynputListener()
    hotkey_listener = GlobalHotkeyListener()
    controller = PynputController()
    file_storage = JsonFileStorage(MACROS_DIR)
    config_store = HotkeyConfigStore(MACROS_DIR)

    recording_service = RecordingService(listener)
    playback_service = PlaybackService(controller)
    persistence_service = PersistenceService(file_storage)
    hotkey_service = HotkeyService(hotkey_listener, config_store, recording_service, playback_service)
    hotkey_service.initialize()
    macro_editor = MacroEditor(recording_service, playback_service)

    api = MacroApi(
        recording_service=recording_service,
        playback_service=playback_service,
        persistence_service=persistence_service,
        hotkey_service=hotkey_service,
        macro_editor=macro_editor,
    )
    return api, hotkey_service


def main():
    api, hotkey_service = build_services()

    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        index_path.write_text(
            "<html><body><h1>Easy Macro Recorder</h1><p>Frontend not built yet.</p></body></html>",
            encoding="utf-8",
        )

    window = webview.create_window(
        title="Easy Macro Recorder",
        url=str(index_path),
        js_api=api,
        width=800,
        height=600,
        min_size=(600, 400),
    )

    try:
        webview.start(debug=False)
    finally:
        hotkey_service.shutdown()


if __name__ == "__main__":
    main()
