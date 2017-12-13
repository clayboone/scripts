#!/bin/bash

if [ "$#" -ne 1 ];
then
	echo "Usage: $0 <script_name.sh>"
	exit 1
fi

if [ -f $1 ];
then
	echo "file \"$1\" already exists. Exiting."
	exit 2
fi

# note this uses a bashism $()
filetype=$(echo $1 | cut -d '.' -f '2-')

case $filetype in
	"rb")
		shebang_line="#!/usr/bin/env ruby"
		;;
	"py")
		shebang_line="#!/usr/bin/env python3"
		;;
	"sh")
		shebang_line="#!/bin/bash"
		;;
	*)
		if [ -t 0 ]; then
			echo "I don't understand that filetype yet!"
			exit 1
		fi
		;;
esac

if [ -t 0 ]; then
	echo $shebang_line >> $1
else
	while read -r input_line ; do
		echo $input_line >> $1
	done
fi
chmod +x $1
