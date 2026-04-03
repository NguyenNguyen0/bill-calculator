# -*- mode: python ; coding: utf-8 -*-

import os

import pyfiglet


pyfiglet_path = os.path.dirname(pyfiglet.__file__)
icon_path = os.path.join("assets", "icon.ico")
icon = icon_path if os.path.exists(icon_path) else None


a = Analysis(
    ['bills_calculator/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(pyfiglet_path, 'fonts'), 'pyfiglet/fonts'),
    ],
    hiddenimports=['pyfiglet.fonts'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bills_calculator',
    icon=icon,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
