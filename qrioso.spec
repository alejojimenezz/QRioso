# qrioso.spec
# For PyInstaller >= 6.0  |  mode: --onefile
# Use:
#   Windows:  pyinstaller qrioso.spec
#   Linux:    pyinstaller qrioso.spec
#
# Executable in dist/qrioso  (Linux)
#               dist/qrioso.exe  (Windows)

import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*.ico', 'assets'),         # Windows
        ('assets/*.png', 'assets'),         # Linux
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'qrcode.image.svg',
        'qrcode.image.pure',
        'segno',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pip',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='qrioso',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if sys.platform == 'win32' else 'assets/icon.png',
)