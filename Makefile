ifeq ($(OS), Windows_NT)
	ifeq ($(PROCESSOR_ARCHITEW6432), AMD64)
		ARCH="64bit"
	else
		ifeq ($(PROCESSOR_ARCHITECTURE), AMD64)
			ARCH="64bit"
		else
			ifeq ($(PROCESSOR_ARCHITECTURE), x86)
				ARCH="32bit"
			endif
		endif
	endif
	SYSTEM="WINDOWS"
else
	UNAME_S := $(shell uname -s)
	UNAME_M := $(shell uname -m)
	ifeq ($(UNAME_S), Linux)
		ifeq ($(UNAME_M), x86_64)
			ARCH="64bit"
		else
			ARCH="32bit"
		endif
		SYSTEM="LINUX"
	endif
	ifeq ($(UNAME_S), Darwin)
		SYSTEM="MAC"
	endif
endif

all: clean dist installer

clean:
	rm -rf build dist

dist:
	@if [ $(SYSTEM) == "WINDOWS" ]; then \
	pyinstaller -y win.spec; \
	fi
	@if [ $(SYSTEM) == "MAC" ]; then \
	pyinstaller -y mac.spec; \
	sed -i .old -e 's/<\/dict>/<key>NSHighResolutionCapable<\/key>\'\
	$$'\n<string>1<\\/string>\\\n<\\/dict>/g' \
	dist/CGHAssemble.app/Contents/Info.plist; \
	rm -f dist/CGHAssemble.app/Contents/Info.plist.old; \
	fi

installer:
	@if [ $(SYSTEM) == "WINDOWS" ]; then \
	makensis install.nsi; \
	fi

.PHONY: all clean dist installer
