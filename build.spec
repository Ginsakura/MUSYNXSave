# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['Launcher.py'],
    pathex=[],
    binaries=[
        ('mscorlib.dll', '.'),
        ('musync_data/Musync.ico', 'musync_data'),
        ('musync_data/LXGW.ttf', 'musync_data'),
        ('musync_data/Assembly-CSharp.dll', 'musync_data')
    ],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('How_to_use.zh.md', '.'),
        ('changelog.md', '.'),
        ('musync_data/songname.update', 'musync_data')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

WithConsole = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MusyncSaveDecode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['musync_data\\Musync.ico'],
)
WithConsoleColl = COLLECT(
    WithConsole,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusyncSaveDecode',
)

WithConsoleAllInOne = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    exclude_binaries=False,
    name='MusyncSaveDecode',
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
    icon=['musync_data\\Musync.ico'],
)

WithoutConsole = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MusyncSaveDecode',
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
    icon=['musync_data\\Musync.ico'],
)
WithoutConsoleColl = COLLECT(
    WithoutConsole,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusyncSaveDecode',
)

WithoutConsoleAllInOne = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    exclude_binaries=False,
    name='MusyncSaveDecode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['musync_data\\Musync.ico'],
)
