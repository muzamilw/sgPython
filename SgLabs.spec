# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['/Users/JanatFarooq/Documents/GitHub/sgPython/main.py'],
             pathex=['/Users/JanatFarooq/Documents/GitHub/sgPython'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SgLabs',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,Tree('/Users/JanatFarooq/Documents/GitHub/sgPython/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SgLabs')
app = BUNDLE(coll,
             name='SgLabs.app',
             icon=None,
             bundle_identifier=None)
