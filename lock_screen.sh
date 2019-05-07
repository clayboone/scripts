#!/bin/bash

FEH_SAVE="$HOME/.fehbg"
PREFIX="/tmp/screenlock-"

# Grep out the current wallpaper assuming it was set with feh
wallpaper=$(grep feh $FEH_SAVE | awk -F"'" '{ print $2 }')
lockpaper="$PREFIX$(basename $wallpaper)"

# If we haven't already made a blurred version of the image
[ ! -f $lockpaper ] && \
    convert $wallpaper -blur 20x20 -scale 1366x768 $lockpaper

# Lock the screen with the blurred image
exec i3lock --image=$lockpaper

