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
    ['src/main.py'],                        # punto de entrada
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*.ico', 'assets'),         # ícono Windows
        ('assets/*.png', 'assets'),         # ícono Linux / preview
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',              # necesario para Pillow + Tkinter
        'qrcode.image.svg',                 # backend SVG de qrcode
        'qrcode.image.pure',
        'segno',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',                           # no incluir herramientas de dev
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
    upx=True,                               # comprime el binario (requiere UPX instalado)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                          # False = sin ventana de consola al abrir
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # ── Ícono por plataforma ───────────────────────────────────────────────────
    icon='assets/icon.ico' if sys.platform == 'win32' else 'assets/icon.png',
)
