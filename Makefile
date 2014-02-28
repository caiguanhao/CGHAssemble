__VERSION__=1.0.4.0
user=choigoonho
repo=maijie
__USER_REPO__=$(user)/$(repo)
__USER_REPO_NAME__=$(user)-$(repo)

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
	NODE=node.exe
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
	NODE=node
endif

BIT=$(subst bit,,$(ARCH))

APP_NAME=CGHAssemble ($(__USER_REPO_NAME__))
APP_ZIP_FILE=CGHAssemble-$(__USER_REPO_NAME__)-$(__VERSION__)-MacOSX.zip

DEB_NAME=cgh-assemble-$(__USER_REPO_NAME__)
DEB_FILE=$(DEB_NAME)-$(__VERSION__)

SETUP_EXE=CGHAssemble-$(__USER_REPO_NAME__)-$(__VERSION__)-win$(BIT)-setup.exe

NODE_MODULES=npm grunt-cli

export DEBFULLNAME=Choi Goon-ho
export DEBEMAIL=caiguanhao@gmail.com

NODE_SHASUM=$(shell python -sBc "import hashlib;\
print hashlib.sha1(open('$(NODE)','rb').read()).hexdigest()")

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
	echo Start building with these info in 2 seconds...; \
	echo user = $(user); \
	echo repo = $(repo); \
	sleep 2; \
	make revert_main_py; \
	for file in "main.py"; do \
	sed -i".bak" \
	-e "s#{{USER}}#$(user)#g" \
	-e "s#{{REPO}}#$(repo)#g" \
	-e "s#{{NODE_SHASUM}}#$(NODE_SHASUM)#g" \
	"$${file}"; \
	echo "Updated $${file}"; \
	done; \
	make clean dist installer finish hash; \
	fi

revert_main_py:
	@if [ -f "main.py.bak" ]; then \
	mv "main.py.bak" "main.py"; \
	fi

finish:
	make revert_main_py

clean:
	rm -rf build dist

dist:
	@if [ "$(SYSTEM)" = "WINDOWS" ]; then \
	pyinstaller -y win.spec; \
	fi
	@if [ "$(SYSTEM)" = "MAC" ]; then \
	pyinstaller -y mac.spec; \
	sed -i .old -e 's/<\/dict>/<key>NSHighResolutionCapable<\/key>\'\
	$$'\n<string>1<\\/string>\\\n<\\/dict>/g' \
	dist/CGHAssemble.app/Contents/Info.plist; \
	rm -f dist/CGHAssemble.app/Contents/Info.plist.old; \
	fi
	@if [ "$(SYSTEM)" = "LINUX" ]; then \
	pyinstaller -y linux.spec; \
	fi

installer:
	@if [ "$(SYSTEM)" = "WINDOWS" ]; then \
	echo "Start building installer in 2 seconds..." && sleep 2; \
	mv "dist/CGHAssemble" "dist/$(APP_NAME)"; \
	sed -i".bak" \
	-e "s#{{APP_NAME}}#$(APP_NAME)#g" \
	-e "s#{{ARCH}}#$(BIT)#g" \
	-e "s#{{PACKAGE}}#$(__USER_REPO_NAME__)#g" \
	-e "s#{{FILENAME}}#$(SETUP_EXE)#g" \
	-e "s#{{VERSION}}#$(__VERSION__)#g" \
	"install.nsi"; \
	makensis install.nsi; \
	mv install.nsi.bak install.nsi; \
	fi
	@if [ "$(SYSTEM)" = "MAC" ]; then \
	rm -f "dist/$(APP_ZIP_FILE)"; \
	mv "dist/CGHAssemble.app" "dist/$(APP_NAME).app"; \
	cd dist && zip "$(APP_ZIP_FILE)" -r "$(APP_NAME).app"; \
	fi
	@if [ "$(SYSTEM)" = "LINUX" ]; then \
	make deb; \
	fi

deb:
	rm -rf dist/$(DEB_FILE)*
	cp -rf dist/CGHAssemble dist/$(DEB_FILE)
	(cd dist/$(DEB_FILE) && find * -type f -exec echo {} \
	opt/$(DEB_NAME)/{} \; | sed 's/\(.*\)\/.*/\1/g' > ../../debian/install)

	sed \
	-e "s#{{PACKAGE}}#$(DEB_NAME)#" \
	-e "s#{{REPO}}#$(__USER_REPO__)#" \
	debian/CGHAssemble.desktop > dist/$(DEB_FILE)/$(DEB_NAME).desktop
	echo "$(DEB_NAME).desktop usr/share/applications" >> debian/install

	for icon in $$(cd res && find hicolor -name "*.png"); do \
	mkdir -p dist/$(DEB_FILE)/$${icon%/*}; \
	cp res/$$icon dist/$(DEB_FILE)/$${icon%/*}/$(DEB_NAME).png; \
	echo "$${icon%/*}/$(DEB_NAME).png usr/share/icons/$${icon%/*}" \
	>> debian/install; \
	done

	(cd dist/$(DEB_FILE) && echo | dh_make --single --createorig)
	mv debian/install dist/$(DEB_FILE)/debian/install
	sed \
	-e "s/{{PACKAGE}}/$(DEB_NAME)/" \
	-e "s/{{ARCH}}/$$(dpkg --print-architecture)/" \
	debian/control > dist/$(DEB_FILE)/debian/control
	cp debian/rules   dist/$(DEB_FILE)/debian/rules
	(cd dist/$(DEB_FILE) && debuild --no-lintian -us -uc)

hash:
	@if [ "$(SYSTEM)" = "WINDOWS" ]; then \
	(echo "import hashlib"; \
	 echo "file = 'dist/$(SETUP_EXE)'"; \
	 echo "def hash(m):"; \
	 echo "  return getattr(hashlib, m)(open(file, 'rb').read()).hexdigest()"; \
	 echo "print '  checksums of', file"; \
	 echo "print '  shasum: \"%s\"' % hash('sha1')"; \
	 echo "print '  md5sum: \"%s\"' % hash('md5')"; \
	) | python; \
	fi
	@if [ "$(SYSTEM)" = "MAC" ]; then \
	echo "  shasum: \"$$(shasum dist/$(APP_ZIP_FILE) | cut -c 1-40)\""; \
	echo "  md5sum: \"$$(md5 -q dist/$(APP_ZIP_FILE))\""; \
	fi
	@if [ "$(SYSTEM)" = "LINUX" ]; then \
	echo "  shasum: \"$$(shasum dist/*.deb | cut -c 1-40)\""; \
	echo "  md5sum: \"$$(md5sum dist/*.deb | cut -c 1-32)\""; \
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

UglifyJS:
	@if [ ! -f "./$(NODE)" ]; then \
	echo "Local node is not found. Run ./configure first."; \
	exit 1; \
	fi
	@if [ ! -f "./uglify-js/bin/uglifyjs" ]; then \
	echo "Local uglify-js is not found. Run ./configure first."; \
	exit 1; \
	fi
	@for f in `find $(NODE_MODULES) -name "*.js"`; \
	do \
	echo "[ Uglifying ] $$f"; \
	./$(NODE) "./uglify-js/bin/uglifyjs" $$f > $$f.minifiedjs 2>/dev/null; \
	if [ ! -s "$$f.minifiedjs" ]; then \
	echo "[  Warning  ] It seems $$f cannot be uglified. Skipped."; \
	fi; \
	done
	@for f in `find $(NODE_MODULES) -name "*.minifiedjs"`; \
	do \
	if [ -s $$f ]; then \
	mv $$f $${f%.*}; \
	else \
	rm -f $$f; \
	fi; \
	done

.PHONY: all clean dist installer hash version CleanNodeModules UglifyJS \
	revert_main_py finish
