#!/usr/bin/env bash
#
# Easy Macro Recorder — Linux Setup
# Installs system deps (if needed), creates venv, installs Python deps.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
REQ_FILE="${SCRIPT_DIR}/macro_app/requirements.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }

# ── Detect distro ──────────────────────────────────────────────────
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "${ID}"
    else
        echo "unknown"
    fi
}

# ── Install system packages ────────────────────────────────────────
install_system_deps() {
    local distro
    distro=$(detect_distro)
    info "Detected distro: ${distro}"

    case "$distro" in
        ubuntu|debian|linuxmint|pop|zorin)
            info "Installing system packages via apt..."
            sudo apt update -qq
            sudo apt install -y \
                python3-gi \
                gir1.2-webkit2-4.1 \
                python3-xlib \
                2>/dev/null || {
                    warn "Some packages may not be available. Trying alternative webkit package..."
                    sudo apt install -y python3-gi gir1.2-webkit2-4.0 python3-xlib 2>/dev/null || true
                }
            ;;
        fedora)
            info "Installing system packages via dnf..."
            sudo dnf install -y \
                python3-gobject \
                webkit2gtk4.1 \
                python3-xlib \
                2>/dev/null || true
            ;;
        arch|manjaro|endeavouros)
            info "Installing system packages via pacman..."
            sudo pacman -S --needed --noconfirm \
                python-gobject \
                webkit2gtk-4.1 \
                python-xlib \
                2>/dev/null || true
            ;;
        opensuse*|sles)
            info "Installing system packages via zypper..."
            sudo zypper install -y \
                python3-gobject \
                webkit2gtk4-1-devel \
                python3-xlib \
                2>/dev/null || true
            ;;
        *)
            warn "Unknown distro (${distro}). Install these manually:"
            warn "  - python3-gobject (PyGObject/GTK bindings)"
            warn "  - gir1.2-webkit2-4.1 (WebKit2 GTK GI bindings)"
            warn "  - python3-xlib (X11 bindings for pynput)"
            ;;
    esac
}

# ── Create venv ────────────────────────────────────────────────────
create_venv() {
    if [ -d "${VENV_DIR}" ]; then
        warn "Virtual environment already exists at ${VENV_DIR}"
        read -p "Recreate it? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "${VENV_DIR}"
        else
            info "Keeping existing venv"
            return
        fi
    fi

    info "Creating virtual environment with --system-site-packages..."
    python3 -m venv --system-site-packages "${VENV_DIR}"
    ok "Virtual environment created"
}

# ── Install Python deps ────────────────────────────────────────────
install_python_deps() {
    info "Installing Python dependencies..."
    "${VENV_DIR}/bin/pip" install --upgrade pip -q
    "${VENV_DIR}/bin/pip" install -r "${REQ_FILE}" -q
    ok "Python dependencies installed"
}

# ── Verify ─────────────────────────────────────────────────────────
verify() {
    info "Verifying installation..."

    local failed=0

    "${VENV_DIR}/bin/python" -c "
import sys
checks = [
    ('pynput',       'from pynput import keyboard, mouse'),
    ('pywebview',    'import webview'),
    ('python-xlib',  'import Xlib'),
]
for name, stmt in checks:
    try:
        exec(stmt)
        print(f'  {name}: OK')
    except ImportError as e:
        print(f'  {name}: FAIL ({e})')
        sys.exit(1)

# GTK check (system package)
try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('WebKit2', '4.1')
    from gi.repository import Gtk, WebKit2
    print('  GTK3 + WebKit2: OK')
except Exception as e:
    print(f'  GTK3 + WebKit2: FAIL ({e})')
    print()
    print('  Install system packages:')
    print('    Ubuntu/Debian: sudo apt install python3-gi gir1.2-webkit2-4.1')
    print('    Fedora:        sudo dnf install python3-gobject webkit2gtk4.1')
    print('    Arch:          sudo pacman -S python-gobject webkit2gtk-4.1')
    sys.exit(1)

print()
print('All checks passed!')
"
    if [ $? -eq 0 ]; then
        ok "Installation verified successfully"
    else
        fail "Verification failed — check errors above"
        exit 1
    fi
}

# ── Main ───────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   Easy Macro Recorder — Linux Setup     ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""

    install_system_deps
    create_venv
    install_python_deps
    verify

    echo ""
    ok "Setup complete! Run the app with:"
    echo ""
    echo "    ./run.sh"
    echo ""
}

main "$@"
