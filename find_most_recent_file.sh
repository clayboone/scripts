#!/bin/sh

if [ "$#" -ne 1 ]
then
	echo "Usage: $0 <base_path>"
	exit 1
fi

find $1 -type f -exec stat --format '%Y :%y %n' "{}" \; | sort -nr | cut -d: -f2- | head
