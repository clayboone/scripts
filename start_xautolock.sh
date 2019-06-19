#!/bin/bash

XAUTOLOCK=/usr/bin/xautolock

# Kill xautolock because it stops working without crashing sometimes
${XAUTOLOCK} -exit

sleep 1

# Start xautolock
${XAUTOLOCK} -time 5 -detectsleep -locker ${HOME}/scripts/auto_lock_screen.sh -nowlocker ${HOME}/scripts/lock_screen.sh &
