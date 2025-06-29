# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['DrinkReminder.py'],
    pathex=[],
    binaries=[],
    datas=[('water.ico', '.'), ('water_data.json', '.')],
    hiddenimports=[
        'winotify',
        'win10toast_click', 
        'win10toast',
        'subprocess',
        'winreg',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui'
    ],
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
    [],
    exclude_binaries=True,
    name='DrinkReminder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['water.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DrinkReminder',
)
