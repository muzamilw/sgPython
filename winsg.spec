# -*- mode: python -*-

import os
from os.path import join

from kivy import kivy_data_dir
#from kivy.deps import sdl2, glew
from kivy_deps import sdl2, glew
from kivy.tools.packaging import pyinstaller_hooks as hooks
from kivymd import hooks_path as kivymd_hooks_path

block_cipher = None
kivy_deps_all = hooks.get_deps_all()
kivy_factory_modules = hooks.get_factory_modules()

datas = [
    (join('userdata', '*.ini'), 'userdata')
]

# list of modules to exclude from analysis
excludes_a = ['Tkinter', 'twisted', 'pygments']    #'_tkinter'

# list of hiddenimports
hiddenimports = kivy_deps_all['hiddenimports'] + kivy_factory_modules  + ['win32timezone'] + ['pkg_resources.py2_warn'] + ['pandas._libs.tslibs.timedelta'] + ['backend_kivy'] + ["requests"] + ["numpy"] + ["pandas"] + ["email.mime"] + ["email.mime.multipart"] + ["email.mime.text"] + ["instagram_private_api"] + ["kivymd"] + ["kivymd.app"] + ["kivymd.uix.button"] + ["schedule"]+ ["kivy.garden"] + ["matplotlib"] + ["customFunctions"] +  ["apiWrappers"] + ["botLogic"] + ["ready"] + ["home"] + ["kivy.garden.matplotlib.backend_kivyagg"] + ["progressbar"] + ["iglogin"] + ["login"]

# binary data
sdl2_bin_tocs = [Tree(p) for p in sdl2.dep_bins]
glew_bin_tocs = [Tree(p) for p in glew.dep_bins]
bin_tocs = sdl2_bin_tocs + glew_bin_tocs

# assets
kivy_assets_toc = Tree(kivy_data_dir, prefix=join('kivy_install', 'data'))
source_assets_toc = Tree('data', prefix='data')
assets_toc = [kivy_assets_toc, source_assets_toc]

tocs = bin_tocs + assets_toc

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
          name='SocialGrowthApi',
          exclude_binaries=True,
          icon=join('data', 'sg.ico'),
          debug=True,
          strip=False,
          upx=True,
          console=True)


coll = COLLECT(exe1,Tree('C:\\Development\\IGBot\\dist\\'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *tocs,
               strip=False,
               upx=True,
               name='SocialGrowthApi')