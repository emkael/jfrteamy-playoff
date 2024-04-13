# -*- mode: python -*-

import os

block_cipher = None

icon_path = os.path.join('jfr_playoff', 'gui', 'icons')
datas = [(icon_path, os.path.join('res', 'icons'))]

a = Analysis(['gui.py'],
             pathex=[SPECPATH],
             datas=datas,
             hiddenimports=['mysql.connector.locales.eng.client_error'],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
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
          name='playoff-gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon=os.path.join(icon_path, 'playoff.ico'),
          version='.version')
