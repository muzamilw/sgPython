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
             hiddenimports= kivy_deps_all['hiddenimports'] + kivy_factory_modules + ['pkg_resources.py2_warn'] + ['backend_kivy'] + ["requests"] + ["numpy"] + ["pandas"] + ["email.mime"] + ["email.mime.multipart"] + ["email.mime.text"] + ["instagram_private_api"] + ["kivymd"] + ["kivymd.app"] + ["kivymd.uix.button"] + ["schedule"]+ ["kivy.garden"] + ["matplotlib"] + ["customFunctions"] +  ["apiWrappers"] + ["botLogic"] + ["ready"] + ["home"] + ["kivy.garden.matplotlib.backend_kivyagg"] + ["progressbar"] + ["iglogin"] + ["login"] + ["gender"] ,
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=[ 'Tkinter', 'enchant', 'twisted','pygments'],   #'_tkinter',
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.binaries = a.binaries - TOC([('libpng16.16.dylib',None,None)])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='start',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

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