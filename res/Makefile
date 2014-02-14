FILE=hammer
SET=$(FILE).iconset
CGHA=CGHAssemble

all:
	@echo "This is a Makefile to generate icons.\n"
	@echo "  make clean                 - to remove any generated files"
	@echo "\nOn Mac OS X:\n"
	@echo "  make iconset icns          - to make .icns"
	@echo "  make iconset optimize icns - if you have ImageOptim installed"
	@echo "\nOn Linux:\n"
	@echo "  make icons                 - to make icons in different sizes"
	@echo "  make icons pngcrush        - if you have pngcrush installed"

clean:
	rm -rf "$(SET)" "$(FILE).icns"

iconset:
	mkdir -p "$(SET)"
	sips -z 16 16   "$(FILE).png" --out "$(SET)/icon_16x16.png"   > /dev/null
	sips -z 32 32   "$(FILE).png" --out "$(SET)/icon_32x32.png"   > /dev/null
	sips -z 128 128 "$(FILE).png" --out "$(SET)/icon_128x128.png" > /dev/null
	sips -z 256 256 "$(FILE).png" --out "$(SET)/icon_256x256.png" > /dev/null
	sips -z 512 512 "$(FILE).png" --out "$(SET)/icon_512x512.png" > /dev/null

	cp   "$(SET)/icon_32x32.png"   "$(SET)/icon_16x16@2x.png"
	sips -z 64 64  "$(FILE).png" --out "$(SET)/icon_32x32@2x.png" > /dev/null
	cp   "$(SET)/icon_256x256.png" "$(SET)/icon_128x128@2x.png"
	cp   "$(SET)/icon_512x512.png" "$(SET)/icon_256x256@2x.png"
	cp   "$(FILE).png"             "$(SET)/icon_512x512@2x.png"

optimize:
	/Applications/ImageOptim.app/Contents/MacOS/ImageOptim "$(SET)"

icns:
	iconutil -c icns "$(SET)"

icons:
	for size in 16x16 32x32 48x48 128x128 256x256; do \
	mkdir -p "hicolor/$$size/apps"; \
	convert "$(FILE).png" -resize $$size! \
	"hicolor/$$size/apps/$(CGHA).png"; \
	done

pngcrush:
	find hicolor -name "*.png" -exec pngcrush -rem cHRM -rem gAMA -rem iCCP \
	-rem sRGB -q {} {}.new \;
	for file in $$(find hicolor -name "*.png.new"); do \
	mv $$file $${file%.*}; \
	done

.PHONY: clean iconset optimize icns
