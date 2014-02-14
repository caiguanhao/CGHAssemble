__VERSION__="1.0.1.0"

MAC_APP_ZIP_FILE_NAME="CGHAssemble-MacOSX.zip"

NODE_MODULES=npm grunt-cli

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

all:
	@if [ ! -z "$(version)" ]; then \
	echo Current Version: $(__VERSION__); \
	for file in "install.nsi" "mac.spec" "main.py" "Makefile" "README.md"; do \
	sed "s/$(__VERSION__)/$(version)/g" "$${file}" > "$${file}.new"; \
	mv "$${file}.new" "$${file}"; \
	echo "Updated version number in $${file}"; \
	done; \
	echo Current Version: $(version); \
	else \
	make clean CleanNodeModules dist installer hash; \
	fi

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
	@echo "To update version number, run: make version=<new-version>";

CleanNodeModules:
	du -sh $(NODE_MODULES)
	# Remove all tests
	find $(NODE_MODULES) -type d -name test | xargs rm -rf

	# Remove all docs
	find $(NODE_MODULES) -type d -name doc | xargs rm -rf

	# Remove all manuals
	find $(NODE_MODULES) -type d -name man | xargs rm -rf

	# Remove all examples
	find $(NODE_MODULES) -type d -name example | xargs rm -rf
	find $(NODE_MODULES) -type d -name examples | xargs rm -rf

	# Remove all images
	find $(NODE_MODULES) -type d -name images | xargs rm -rf

	# Remove dot files
	find $(NODE_MODULES) -name ".npmignore" -o -name ".travis.yml" |\
	xargs rm -rf

	# Remove README
	find $(NODE_MODULES) -name "README.md" | xargs rm -rf

	# Other files
	rm -rf npm/html
	du -sh $(NODE_MODULES)

.PHONY: all clean dist installer hash version CleanNodeModules
