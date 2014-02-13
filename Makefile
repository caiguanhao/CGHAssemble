__VERSION__="1.0.1.0"

MAC_APP_ZIP_FILE_NAME="CGHAssemble-MacOSX.zip"

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

all: clean dist installer hash

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
	@if [ $(SYSTEM) == "MAC" ]; then \
	rm -f $(MAC_APP_ZIP_FILE_NAME); \
	cd dist && zip ../$(MAC_APP_ZIP_FILE_NAME) -r CGHAssemble.app; \
	fi

hash:
	@if [ $(SYSTEM) == "MAC" ]; then \
	echo "  shasum: \"$$(shasum $(MAC_APP_ZIP_FILE_NAME) | cut -c 1-40)\""; \
	echo "  md5sum: \"$$(md5 -q $(MAC_APP_ZIP_FILE_NAME))\""; \
	fi

version:
	@echo Current Version: $(__VERSION__)
	@if [ -z "$(VERSION)" ]; then \
	echo "To update version number, run: make VERSION=<new-version> version"; \
	else \
	for file in "install.nsi" "mac.spec" "main.py" "Makefile" "README.md"; do \
	sed "s/$(__VERSION__)/$(VERSION)/g" "$${file}" > "$${file}.new"; \
	mv "$${file}.new" "$${file}"; \
	echo "Updated version number in $${file}"; \
	done; \
	fi

.PHONY: all clean dist installer hash
