# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['client_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # copy the settings file next to the exe
        ('client_settings.json', '.'),
    ],
    hiddenimports=[
        # PyQt6 pulls a lot of plugins at runtime
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtSvg',
        # psycopg2 (binary wheels contain the .dll)
        'psycopg2',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='client',               # <-- final .exe name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                    # compress (optional, needs UPX installed)
    console=False,               # <-- GUI → no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='client.ico'           # <-- put your .ico here (optional)
)