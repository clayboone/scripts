#!/bin/sh

# gnome-terminal custom command like: /path/to/me/start_as_tmux.sh Default

session_name=${1-"Default"}

if tmux has-session -t "${session_name}"; then
    tmux attach-session -t "${session_name}"
else
    tmux new-session -s "${session_name}"
fi
