#!/bin/bash

function sighup_update {
	echo -e "\n---------------------\nCaught reload Signal:"
	~/bin/find_drives.sh
}

trap sighup_update SIGHUP

while (sleep 10); do
	: # nothing lol.. please put GUI here :)
done
