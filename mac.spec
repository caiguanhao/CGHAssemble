a = Analysis(['main.py'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='CGHAssemble',
          debug=False,
          strip=None,
          upx=True,
          console=False)
node = [('node.exe', 'node.exe', 'BINARY')]
npm = Tree('npm', prefix='npm')
grunt_cli = Tree('grunt-cli', prefix='grunt-cli')
a.datas += [
  ('i18n/zh.qm', 'i18n/zh.qm', 'DATA')
]
bundle = BUNDLE(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
                node + npm,
                grunt_cli,
                info_plist={
                  'NSHighResolutionCapable': 'True',
                  'LSBackgroundOnly': '0'
                },
                icon='res/hammer.icns',
                version='1.0.1.0',
                name='CGHAssemble.app')
