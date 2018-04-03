#!/bin/sh
# Easy way to mount the EFI in BSD (possibly port to linux later)
# This should probably just be a function in .oh-my-zsh/custom/

if [ `id -u` -ne 0 ]; then
	echo Got root? 2>&1
	exit 1
fi

if [ ! -d /tmp/efi ]; then
	mkdir /tmp/efi
fi

mount_msdosfs /dev/ada0p2 /tmp/efi
