#!/bin/bash
SCROT=/usr/bin/scrot
CONVERT=/usr/bin/convert
I3LOCK=/usr/bin/i3lock
LOCKPAPER="/tmp/lockpaper.png"

${SCROT} ${LOCKPAPER}
${CONVERT} ${LOCKPAPER} -blur 10x10 ${LOCKPAPER} # ?
${I3LOCK} -i ${LOCKPAPER}
exec rm ${LOCKPAPER}
