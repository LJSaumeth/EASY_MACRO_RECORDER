#!/usr/bin/env bash
#
# Easy Macro Recorder — Run on Linux
# Launches the app using the project virtual environment.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
MAIN="${SCRIPT_DIR}/macro_app/main.py"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ── Check venv exists ──────────────────────────────────────────────
if [ ! -d "${VENV_DIR}" ]; then
    echo -e "${RED}[ERROR]${NC} Virtual environment not found at ${VENV_DIR}"
    echo ""
    echo "Run setup first:"
    echo "    ./setup.sh"
    exit 1
fi

if [ ! -f "${MAIN}" ]; then
    echo -e "${RED}[ERROR]${NC} main.py not found at ${MAIN}"
    exit 1
fi

# ── Check display ──────────────────────────────────────────────────
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
    echo -e "${RED}[ERROR]${NC} No display server detected (DISPLAY and WAYLAND_DISPLAY are empty)"
    echo "This app requires a graphical environment."
    exit 1
fi

# ── Pre-flight check ───────────────────────────────────────────────
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Easy Macro Recorder                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check key dependencies
"${VENV_DIR}/bin/python" -c "
import sys
try:
    import pynput, webview, Xlib
except ImportError as e:
    print(f'[ERROR] Missing dependency: {e}')
    print('Run: ./setup.sh')
    sys.exit(1)
" || exit 1

# ── Detect and warn about Wayland limitations ──────────────────────
if [ "${XDG_SESSION_TYPE:-}" = "wayland" ]; then
    echo -e "${YELLOW}[NOTE]${NC} Wayland session detected."
    echo "  - Global hotkeys work through XWayland"
    echo "  - For best results, run games in X11 mode or use gamescope"
    echo ""
fi

# ── Launch ─────────────────────────────────────────────────────────
echo -e "${GREEN}[START]${NC} Launching Easy Macro Recorder..."
echo -e "${CYAN}[INFO]${NC}  Hotkeys: F6=Record  F7=Play  F8=Stop"
echo -e "${CYAN}[INFO]${NC}  Press Ctrl+C in this terminal to force quit"
echo ""

cd "${SCRIPT_DIR}/macro_app"
exec "${VENV_DIR}/bin/python" main.py "$@"
