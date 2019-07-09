#!/bin/sh
# Display a dialog that a user can cancel. When the dialog is not cancelled,
# power off the computer. Otherwise, abort.

for i in `seq 1 100`
do
    echo $i
    sleep 0.1
done | zenity --progress \
              --auto-close \
              --text="Shutting down..." \
              && poweroff
