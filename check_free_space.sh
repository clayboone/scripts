#!/bin/bash
# alias me to "cs" or similar on linux (bsd uses /dev/ada0 for first disk)

df -h | grep -E '(Avail|sd[b-z])' # dont' include sda
