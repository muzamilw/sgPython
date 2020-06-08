# -*- mode: python ; coding: utf-8 -*-

import os
from os.path import join
from kivy.tools.packaging import pyinstaller_hooks as hooks
from kivy import kivy_data_dir
from kivymd import hooks_path as kivymd_hooks_path

spec_root = os.path.abspath(SPECPATH)
block_cipher = None
app_name='SocialPlannerPro'
mac_icon = 'ml.icns'

kivy_deps_all = hooks.get_deps_all()
kivy_factory_modules = hooks.get_factory_modules()
hiddenimports = kivy_deps_all['hiddenimports'] + kivy_factory_modules + ['pkg_resources.py2_warn']

# assets
kivy_assets_toc = Tree(kivy_data_dir, prefix=join('kivy_install', 'data'))
source_assets_toc = Tree('data', prefix='data')
#source_assets2_toc = Tree('userdata', prefix='userdata')
assets_toc = [kivy_assets_toc, source_assets_toc]

tocs =  assets_toc #+ bin_tocs

a = Analysis(['main.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[('*.kv','.')],
             hiddenimports=hiddenimports,
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted','pygments'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='start',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )

coll = COLLECT(exe,Tree('/Users/JanatFarooq/Documents/GitHub/Notesx/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *tocs,
               strip=False,
               upx=True,
               name=app_name)

app = BUNDLE(exe,
             name=app_name + '.app',
             icon=mac_icon,
             bundle_identifier='com.socialplannerpro.automation.socialplanerpro')