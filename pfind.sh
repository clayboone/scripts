#!/bin/bash
PIDLIST="$(pgrep -i $@)"
[ -n "$PIDLIST" ] && exec ps -p $PIDLIST
