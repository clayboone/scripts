#!/bin/bash
# this file is run by udev when a new device matching [sh]d[a-z] is detected
# (( bash because of bash-specific syntax; sorry :/ ))

PID=$(ps aux | grep catch_hup.sh | grep -v grep | awk '{ print $2 }')

if [ "x$PID" == "x" ]; then
	exit 1 # Front end isn't running. Do nothing.
else
	kill -SIGHUP $PID # no need to loop thru $PID; see ``man kill''
fi

