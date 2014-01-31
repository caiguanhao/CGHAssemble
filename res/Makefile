FILE=hammer
SET=$(FILE).iconset

icons:
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
	open -a ImageOptim "$(SET)"

icns:
	iconutil -c icns "$(SET)"
