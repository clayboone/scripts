#!/bin/bash
for i in {a..z}; do
	if [ -b /dev/sd$i ]; then
		#sernum=$(smartctl -a /dev/sd$i | grep "Serial Number:" | cut -d ":" -f 2 | sed 's/\ //g')
		sernum=$(udevadm info /dev/sd$i | cut -d " " -f "2-" | awk -F "=" '{if ($1=="ID_SERIAL"){ print $2; }}')
		echo Drive /dev/sd$i is $sernum
	fi
done

