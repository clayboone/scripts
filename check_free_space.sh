#!/bin/bash

df -h | grep -E '(Avail|sd[b-z])' # dont' include sda
