#!/bin/bash
SCROT=/usr/bin/scrot
CONVERT=/usr/bin/convert
COMPOSITE=/usr/bin/composite
I3LOCK=/usr/bin/i3lock
LOCKPAPER="/tmp/lockpaper.png"

# Sleep before scrot to try and not catch the i3 bar.
sleep 0.5

${SCROT} ${LOCKPAPER}
${CONVERT} ${LOCKPAPER} -blur 10x10 ${LOCKPAPER}

if [ $# -gt 0 ]
then
    if [ ! -e "$1" ]
    then
        echo "Cannot composite image $1 because file does not exist." >&2
    else
        ${COMPOSITE} -gravity center "$1" ${LOCKPAPER} ${LOCKPAPER}
    fi
fi

${I3LOCK} -i ${LOCKPAPER}
exec rm ${LOCKPAPER}
