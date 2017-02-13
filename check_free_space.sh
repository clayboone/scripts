#!/bin/bash

df -h | egrep '(Avail|sd[b-z])' # dont' include sda
