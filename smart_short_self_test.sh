#!/bin/bash

# print some relevent smart attributes and run a short self test

ARGV0=$(basename $0)
SMARTCTL=$(which smartctl)
STDERR=/dev/stderr

if [ "$#" -ne 1 ]; then
	echo "Usage: $ARGV0 /dev/sdX" >$STDERR
	echo "       Make sure to specify the whole block device and not just a partition." >$STDERR
	echo "       eg. $ARGV0 /dev/sdb" >$STDERR
	exit 1
fi

if [ ! -b $1 ]; then
	echo "$ARGV0: No block device \"$1\" found." >$STDERR
	exit 1
fi

if [ ! -x $SMARTCTL ]; then
	echo "$ARGV0: Can't find smartctl (do you have smartmontools installed?)" >$STDERR
	exit 1
fi

# some important attributes
$SMARTCTL -A $1 | grep -i -E '(power|current|reallocated)' | awk '{ print $10, "\t", $2 }'

# actual scan part
$SMARTCTL -t short $1		# start the test in the background
sleep 140			# make this terminal sleep for about 2 minutes
echo				# We need a blank line for pretty printing (i'm avoiding the word "formatting" here)
$SMARTCTL -l selftest $1	# show results

