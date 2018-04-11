#!/bin/sh
# coding: utf8

# Use scrot to interactively select an area of the screen to capture. Then
# move the captured screenshot to /tmp/scrots, and copy the image data into
# the X clipboard.

SCROT=`which scrot`
XCLIP=`which xclip`
DESTDIR=/tmp/scrots

if [ ! -x "${SCROT}" ]; then
	echo "Please install scrot(1)" >2
	exit 1
fi

if [ ! -d "${DESTDIR}" ]; then
	mkdir -p "${DESTDIR}" || {
		echo "Failed to create \"${DESTDIR}\". Cowardly aborting." >2
		exit 1
	}
	echo "Created ${DESTDIR}..."
fi

# Take scrot, and save filename to a variable
filename=`${SCROT} --select --exec 'echo $f' '%Y-%m-%d-%H%M%S_$wx$h.png'`

# Move to a tmpfs/ramdisk
mv "${filename}" "${DESTDIR}/${filename}" || {
	echo "Failed to move ${filename} to ${DESTDIR}. Quiting" >2
	exit 1
}

# And copy it
if [ -x "${XCLIP}" ]; then
	cat "${DESTDIR}/${filename}" | xclip -i
else
	echo "Unable to locate xclip(1). Skipping." >2
fi

echo "${DESTDIR}/${filename}"
