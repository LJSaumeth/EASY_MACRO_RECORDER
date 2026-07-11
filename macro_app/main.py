import os
import platform
import sys
from pathlib import Path


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


# ── Linux dependency checks ────────────────────────────────────────
def _check_linux_deps():
    """Verify that required system packages are available on Linux."""
    errors = []

    # Check PyGObject (GTK bindings)
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gtk, WebKit2  # noqa: F401
    except ImportError:
        errors.append(
            "Missing GTK/WebKit bindings. Install system packages:\n"
            "  Ubuntu/Debian: sudo apt install python3-gi gir1.2-webkit2-4.1\n"
            "  Fedora:        sudo dnf install python3-gobject webkit2gtk4.1\n"
            "  Arch:          sudo pacman -S python-gobject webkit2gtk-4.1"
        )
    except ValueError:
        # gi imported but WebKit2 version not found — try 4.0 fallback
        try:
            import gi
            gi.require_version("Gtk", "3.0")
            gi.require_version("WebKit2", "4.0")
            from gi.repository import Gtk, WebKit2  # noqa: F401
        except Exception:
            errors.append(
                "WebKit2 4.1 not found. Install:\n"
                "  Ubuntu/Debian: sudo apt install gir1.2-webkit2-4.1\n"
                "  Alternative:   sudo apt install gir1.2-webkit2-4.0"
            )

    # Check python-xlib (needed by pynput for global keyboard hooks)
    try:
        import Xlib  # noqa: F401
    except ImportError:
        errors.append(
            "Missing python-xlib. Install:\n"
            "  Ubuntu/Debian: sudo apt install python3-xlib\n"
            "  Fedora:        sudo dnf install python3-xlib\n"
            "  Arch:          sudo pacman -S python-xlib\n"
            "  Or via pip:    pip install python-xlib"
        )

    return errors


def _print_wayland_notice():
    """Print a notice if running under Wayland."""
    session_type = os.environ.get("XDG_SESSION_TYPE", "")
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

    if session_type == "wayland" or wayland_display:
        print("[INFO] Wayland session detected.")
        print("  - Global hotkeys work through XWayland (requires DISPLAY env)")
        print("  - For gaming, consider running games in X11 mode or use gamescope")
        print("")


def build_services():
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
    # ── Platform-specific preflight ────────────────────────────────
    if platform.system() == "Linux":
        _print_wayland_notice()
        dep_errors = _check_linux_deps()
        if dep_errors:
            print("[ERROR] Missing system dependencies:\n")
            for err in dep_errors:
                print(f"  {err}\n")
            print("Run ./setup.sh from the project root to install everything automatically.")
            sys.exit(1)

    # ── Lazy imports (after dep checks so errors are clear) ─────────
    import webview

    # ── Build services ─────────────────────────────────────────────
    try:
        api, hotkey_service = build_services()
    except Exception as e:
        print(f"[ERROR] Failed to initialize services: {e}")
        if platform.system() == "Linux":
            print("On Linux, make sure python3-xlib is installed:")
            print("  Debian/Ubuntu: sudo apt install python3-xlib")
            print("  Or run: ./setup.sh")
        sys.exit(1)

    # ── Frontend ───────────────────────────────────────────────────
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        index_path.write_text(
            "<html><body><h1>Easy Macro Recorder</h1><p>Frontend not built yet.</p></body></html>",
            encoding="utf-8",
        )

    # ── Launch window ──────────────────────────────────────────────
    try:
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
    except Exception as e:
        hotkey_service.shutdown()
        msg = str(e)
        if "webview" in msg.lower() and ("backend" in msg.lower() or "no" in msg.lower()):
            print("[ERROR] No GUI backend available. pywebview needs GTK or Qt on Linux.")
            print("  GTK: sudo apt install python3-gi gir1.2-webkit2-4.1")
            print("  Qt:  pip install PyQt6")
            print("  Or run: ./setup.sh")
        else:
            print(f"[ERROR] {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
