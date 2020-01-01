a = Analysis(['playoff.py'],
             pathex=[SPECPATH],
             hiddenimports=['mysql.connector.locales.eng.client_error'],
             hookspath=['.'],
             runtime_hooks=None,
             excludes=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='playoff.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          version=".version",
          icon="jfr_playoff/gui/icons/playoff.ico"
         )
