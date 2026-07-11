# PyInstaller spec file for Easy Macro Recorder
# Build: pyinstaller EasyMacroRecorder.spec

import sys
from pathlib import Path

block_cipher = None

frontend_path = str(Path("frontend") / ".")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (frontend_path, "frontend"),
    ],
    hiddenimports=[
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "webview",
        "webview.platforms.winforms",
        "bottle",
        "clr_loader",
        "proxy_tools",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EasyMacroRecorder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="EasyMacroRecorder",
)
