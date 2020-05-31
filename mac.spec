# -*- mode: python -*-

import os
from os.path import join

from kivy import kivy_data_dir
#from kivy.deps import sdl2, glew
#from kivy_deps import sdl2, glew
from kivy.tools.packaging import pyinstaller_hooks as hooks
from kivymd import hooks_path as kivymd_hooks_path

#from kivy.tools.packaging.pyinstaller_hooks import install_hooks
#install_hooks(globals())

block_cipher = None
kivy_deps_all = hooks.get_deps_all()
kivy_factory_modules = hooks.get_factory_modules()

datas = [
    (join('userdata', '*.ini'), 'userdata')
]

# list of modules to exclude from analysis
excludes_a = ['Tkinter', '_tkinter', 'twisted', 'pygments','mypython']

# list of hiddenimports
hiddenimports = kivy_deps_all['hiddenimports'] + kivy_factory_modules + ['pkg_resources.py2_warn']

# binary data
#sdl2_bin_tocs = [Tree(p) for p in sdl2.dep_bins]
#glew_bin_tocs = [Tree(p) for p in glew.dep_bins]
#bin_tocs = sdl2_bin_tocs + glew_bin_tocs

# assets
kivy_assets_toc = Tree(kivy_data_dir, prefix=join('kivy_install', 'data'))
source_assets_toc = Tree('data', prefix='data')
assets_toc = [kivy_assets_toc, source_assets_toc]

tocs =  assets_toc #+ bin_tocs

a = Analysis(['main.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=excludes_a,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


exe1 = EXE(pyz,
          a.scripts,
          name='SPlannerPro',
          exclude_binaries=True,
          icon=join('data', 'sp.ico'),
          debug=False,
          strip=False,
          upx=True,
          console=False)


coll = COLLECT(exe1,Tree('/Users/JanatFarooq/Documents/GitHub/sgPython/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *tocs,
               strip=False,
               upx=True,
               name='SPlannerPro')

app = BUNDLE(exe1,
         name='SocialPlannerPro.app',
         icon=join('data', 'sp.ico'),
         bundle_identifier='SocialPlannerPro',
         info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'My File Format',
                    'CFBundleTypeIconFile': 'MyFileIcon.icns',
                    'LSItemContentTypes': ['com.example.myformat'],
                    'LSHandlerRank': 'Owner'
                    }
                ]
            },)