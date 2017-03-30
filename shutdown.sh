#!/bin/sh
# wait a few seconds and shutdown unless user clicks cancel or hits escape
for i in `seq 1 100`; do echo $i; sleep 0.1; done | zenity --progress --auto-close --text="Shutting down..." && poweroff
