# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Alien Invasion Game

block_cipher = None

a = Analysis(
    ['Visintainer_A_AlienGame.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),           # Include all images
        ('assets', 'assets'),     # Include font files
        ('sounds', 'sounds'),     # Include all sound files
    ],
    hiddenimports=[],
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
    name='AlienInvasion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window (set to True for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file path here if you have one (e.g., 'icon.ico')
)

