#!/bin/sh
# coding: utf8

# A single-line script to upscale my laptop's resolution to something more
# usable

NATIVE="1366x768"
UPSCALE="1920x1080"

xrandr --output LVDS-1 \
    --mode "$NATIVE" \
    --rate 60 \
    --fb "$UPSCALE" \
    --scale-from "$UPSCALE" \
    --panning "$UPSCALE"
