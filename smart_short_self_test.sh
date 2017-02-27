#!/bin/bash

# print some relevent smart attributes and run a short self test

ARGV0="$(basename $0)"
SMARTCTL="$(which smartctl)"
RUBY="$(which ruby)"
STDERR="/dev/stderr"
TMPFILE="$(mktemp)"

if [ "$#" -ne 1 ]; then
	echo "Usage: $ARGV0 <[/dev/] sdX>" >$STDERR
	echo "       Make sure to specify the whole block device and not just a partition." >$STDERR
	echo "       eg. $ARGV0 /dev/sdb" >$STDERR
	echo "Note:  This program _only_ looks for block-special devices in /dev/*" >$STDERR
	exit 1
fi
device="/dev/$(basename $1)"

if [ ! -b $device ]; then
	echo "$ARGV0: No block device \"$device\" found." >$STDERR
	exit 1
fi

if [ ! -x $SMARTCTL ]; then
	echo "$ARGV0: Can't find smartctl (do you have smartmontools installed?)" >$STDERR
	exit 1
fi

if [ ! -x $RUBY ]; then
	echo "$ARGV0: This version requires ruby to be installed and executable from your \$PATH"
	exit 2
fi

# check to see if smartctl is runnable as this user by checking if smart is enabled
# first time we run smartctl, so we'll know if we're root/sudo/setuid here
$SMARTCTL -i $device >$TMPFILE

gotchas=( \
	"Unable to detect device type" \
	"No such device" \
	"Permission denied" \
	"Unknown USB bridge" \
	)

for i in ${gotchas[@]}; do
	error="$(grep \"$i\" <$TMPFILE)"
	if [ $? -eq 0 ]; then
		echo "$ARGV0: $error"
		rm $TMPFILE >/dev/null 2>&1
		exit 1
	fi
done

# basic information
echo -e "Basic device information for $device:\n"
grep -E '(Model|Serial|Capacity|SMART support|SATA Version|Form Factor)' <$TMPFILE
echo

# if smart is not enabled, try to enable it. if i can't, stop here and tell user to enable smart on the device
grep "SMART support is:.*Enabled" <$TMPFILE >/dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "$ARGV0: Attempting to enable SMART on $device..."
	$SMARTCTL -s on $device >/dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo "$ARGV0: Failed. Please enable SMART for this device to continue"
		rm -f $TMPFILE >/dev/null 2>&1
		exit 1
	else
		echo "$ARGV0: SMART has been enabled."
	fi
fi
rm -f $TMPFILE >/dev/null 2>&1

# overall health
echo "--------------------------------------------------"
$SMARTCTL -H $device | grep "^SMART"
echo

# some important attributes
echo -e "--------------------------------------------------\nImportant SMART attributes:\n"
$SMARTCTL -A $device | grep -i -E '(power|temperature|current|reallocated|reported|seek)' | awk '{ print $10, "...\t", $2 }'
echo

# smart error log
# this is probably the least efficient way i can think to do this..
echo -e "--------------------------------------------------\nSmart error log (smartctl -l xerror,error <dev>):"
for cmd in "xerror" "error"; do
	result=$($SMARTCTL -l $cmd $device | grep "ATA Error Count")
	num_errors=$(echo $result | grep -o '[0-9]*$') # i was getting this for something..
	if [ $? -eq 0 ]; then
		echo $result
		$SMARTCTL -l $cmd $device | grep "Error [0-9]* occurred at"
	fi
	unset result
	unset cmd
done

# progress bar helper via https://gist.github.com/ivanalejandro0/9159989
# there was also a super fancy unicode one, but this should support far more distros/OSs
progress(){
    # example usage:
    # progress 30G 9G 30
    # 30G [================>.................................] 30% (9G)

    # params:
    # $1 = total value (e.g.: source size)
    # $2 = current value (e.g.: destination size)
    # $3 = percent completed
    [[ -z $1 || -z $2 || -z $3 ]] && exit  # on empty param...

    percent=$3
    completed=$(( $percent / 2 ))
    remaining=$(( 50 - $completed ))

    echo -ne "\r$1 ["
    printf "%0.s=" `seq $completed`
    echo -n ">"
    [[ $remaining != 0 ]] && printf "%0.s." `seq $remaining` #shouldn't this be -gt or -ge instead of != ?
    echo -n "] $percent% ($2)  "
}

# setup signal handler (ctrl-c, shutdown/reboot, and kill's default)
_term() {
	echo -e "\n$ARGV0: Caught shutdown signal. Attempting to cancel operation"
	_cleanup
}

_int() {
	echo -e "\n$ARGV0: Received user abort. Attempting to cancel operation"
	_cleanup
}

_hup() {
	echo
	result=$(smartctl -l selftest $device | grep -A 1 "^Num" | tail -n 1)
	if [ -z "$result" ]; then
		echo "$ARGV0: No smart tests have been run"
	fi
	# TODO, expound this later, please
	echo $result
}

_cleanup() {
	$SMARTCTL -X $device >/dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo "$ARGV0: Cancelled self-test successfully."
	else
		# TODO this is ugly and not helpful
		echo "$ARGV0 returned $? after asking disk to cancel operation."
	fi

	_hup
	exit 1
}

trap _term SIGTERM
trap _int SIGINT
trap _hup SIGHUP

# actual scan part
echo -e "--------------------------------------------------\nBeginning short self-test now (Ctrl+C to cancel)\n"
run_minutes=$($SMARTCTL -t short $device | grep -o 'Please wait [0-9]*' | cut -d ' ' -f 3)
let run_seconds=60*$run_minutes
for each_second in $(seq $run_seconds -2 0); do
	# show progress
	let cur=$run_seconds-$each_second
	percent=$(echo print "($cur/$run_seconds.0*100).floor" | ruby) # TODO ruby ...
	progress $run_seconds $cur $percent
	# check for error yet
	
	# sleep
	sleep 2
done

_hup
exit 0
