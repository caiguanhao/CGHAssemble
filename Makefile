all: clean dist installer

clean:
	rm -rf build dist

dist:
	pyinstaller -y win.spec

installer:
	makensis install.nsi
