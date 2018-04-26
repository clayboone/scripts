#!/bin/sh
# coding: utf8

# Use scrot to interactively select an area of the screen to capture. Then
# move the captured screenshot to /tmp/scrots, and copy the image data into
# the X clipboard.

SCROT=`which scrot`
XCLIP=`which xclip`
DESTDIR=/tmp/scrots

fatal() {
	echo "$@" 1>&2
	exit 1
}

if [ ! -x "${SCROT}" ]; then
	fatal "Please install scrot(1)"
fi

if [ ! -d "${DESTDIR}" ]; then
	mkdir -p "${DESTDIR}" || \
		fatal "Failed to create \"${DESTDIR}\". Cowardly aborting."
	echo "Created ${DESTDIR}..."
fi

# Take scrot, and save filename to a variable
filename=`sleep 0.2 && \
	${SCROT} --select --exec 'echo -n $f' '%Y-%m-%d-%H%M%S_$wx$h.png'`

if [ -z "$filename" ]; then
	fatal "Failed to scrot!"
fi

# Move to a tmpfs/ramdisk
mv "${filename}" "${DESTDIR}/${filename}"
if [ $? -ne 0 ]; then
	# this check is kinda lame. BSD `sh` reads this particular
	# "return 0" as a failure. i'm not sure why...
	fatal "Failed to move ${filename} to ${DESTDIR}. Quiting"
fi

# And copy it
if [ -x "${XCLIP}" ]; then
	# This next line isn't working... Is it the problem of two clipboards?
	cat "${DESTDIR}/${filename}" | xclip -i -t image/png
else
	echo "Unable to locate xclip(1). Skipping."
fi

echo "${DESTDIR}/${filename}"
