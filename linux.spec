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
node = [('node', 'node', 'BINARY')]
npm = Tree('npm', prefix='npm')
grunt_cli = Tree('grunt-cli', prefix='grunt-cli')
a.datas += [
  ('res/hammer.png', 'res/hammer.png', 'DATA'),
  ('i18n/zh.qm', 'i18n/zh.qm', 'DATA'),
]
collect = COLLECT(exe,
                  a.binaries,
                  a.zipfiles,
                  a.datas,
                  node + npm,
                  grunt_cli,
                  strip=None,
                  upx=True,
                  name='CGHAssemble')
