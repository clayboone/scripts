#!/bin/bash
# test the inetz

TMPFILE=/tmp/$(whoami)-$(basename $0).tmp
ALLGOOD=y

# check depends
NMCLI=$(which nmcli)
WGET=$(which wget)
NPING=$(which nping)
MTR=$(which mtr)
PING=$(which ping)

# some basic tests
echo -e "Starting basic tests..."


#default gateway?
echo -en "Ping local gateway\t"
s=$(route -n | grep "^0.0.0.0" | awk '{ print $2 }');
$PING -c 1 $s >/dev/null 2>&1; r=$?;
if [ $r -eq 0 ]; then
	echo -ne "OK"; 
else
	echo -ne "NOT OK"; 
	ALLGOOD="n";
fi; 
echo -e "\t(${s:-"No Gateway"})"

#google dns servers?
s=8.8.8.8; 
$PING -c 1 $s >/dev/null 2>&1; 
if [ $? -eq 0 ]; then 
	echo -e "Inet L3 $PING\tOK\t($s)"; 
else 
	echo -e "Inet L3 $PING\tNOT OK\t($s)"; 
	ALLGOOD="n";
fi; 

# old-style nameserver?
s=$(grep -i nameserver /etc/resolv.conf | awk '{ print $2 }'); 
$PING -c 1 $s >/dev/null 2>&1; 
if [ $? -eq 0 ]; then 
	echo -e "Nameserver\tOK\t($s via /etc/resolv.conf)"; 
else 
	echo -e "Nameserver\tNOT OK\t($s via /etc/resolv.conf)"; 
	ALLGOOD="N";
fi; 

# new-style nameserver?
if [ "x$NMCLI" == "x" ]; then 
	echo "Network manager not installed (time to upgrade Linux?)"; 
else 
	s=$($NMCLI dev show | grep "IP4\.DNS" | awk '{ print $2 }'); 
	$PING -c 1 $s >/dev/null 2>&1; 
	if [ $? -eq 0 ]; then 
		echo -e "Nameserver\tOK\t($s via $NMCLI)"; 
	else
		echo -e "Nameserver\tNOT OK\t(${s:-"NO ADDRESS"} via $NMCLI)";
		ALLGOOD="n";
	fi;
fi;	

# can we resolve and connect to web via google.com?
s=$(host -t A google.com | grep "has address" | head -n 1 | awk '{ print $4 }'); 
if [ "x$s" == "x" ]; then
	echo -e "Inet L7 DNS\tNOT OK\t(Unable to resolve google.com)"
	$PING -c 1 74.125.129.102 >/dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo -e "Google.com\tOK\t(74.125.129.102 via hard-coded address is reachable)"
	else
		echo -e "Google.com\tNOT OK\t(74.125.129.102 via hard-coded address is unreachable)"
		ALLGOOD="n";

	fi
else
	echo -e "Inet L7 DNS\tOK\t(Resolved google.com to $s)"
	$NPING -c 1 --tcp-connect $s -p 443 >/dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo -e "Inet L7 HTTPS\tOK\t(TCP connect to https://google.com successful)"
	else
		echo -e "Inet L7 HTTPS\tNOT OK\t(TCP connect to https://google.com unsuccessful)"
		ALLGOOD="n";

	fi
fi

# some extended tests

if [ $ALLGOOD == "n" ]; then
	echo -e "\nSome basic tests failed. Exiting."
	exit 1	
else
	echo -e "\nSome extended tests..."
fi

# download something over http


# check NTP time vs local time for https


# download something over https




# $PING flood to default gateway (local)
s=$(route -n | grep "^0.0.0.0" | awk '{ print $2 }');
if [ "$(id -u)" -eq 0 ]; then
	echo -ne "Fast local $PING flood ($s):\t"
	$PING -q -c  50 -f $s | grep "packet loss" | \
		awk '{ print $4 " out of " $1 " received (" $6 " loss)" }'
else
	echo -ne "Slow local $PING flood ($s):\t"
	$PING -q -c 25 -f -i 0.2 8.8.8.8 | grep "packet loss" | \
		awk '{ print $4 " out of " $1 " received (" $6 " loss)" }'
fi

# $PING flood to google dns (remote)
if [ "$(id -u)" -eq 0 ]; then
	echo -ne "Fast remote $PING flood (8.8.8.8):\t"
	$PING -q -c 50 -f 8.8.8.8 | grep "packet loss" | \
		awk '{ print $4 " out of " $1 " received (" $6 " loss)" }'
else
	echo -ne "Slow remote $PING flood (8.8.8.8):\t"
	$PING -q -c 25 -f -i 0.2 8.8.8.8 | grep "packet loss" | \
		awk '{ print $4 " out of " $1 " received (" $6 " loss)" }'
fi

#mtr (if found) or traceroute/path for multiple NAT, etc
if [ "x$MTR" == "x" ]; then
	echo -e "mtr not found. Giving up." # maybe i'll add traceroute/tracepath later. i like mtr
else
	echo -ne "Hops to Google DNS:\t\t\t"
	$MTR -4nlc 1 google.com | grep "^h" | awk '{ print $3 }' >$TMPFILE
	hops_text=$(wc -l $TMPFILE | awk '{ print $1 }')
	let hops="$hops_text - 1" #mtr adds an extra hop on the end? i hope subtracting 1 is ok :S
	echo -e "$hops"
	
	echo -e "First 5 hops outbound:\t\t\t$(cat $TMPFILE | head -n 1)"
	for i in $(cat $TMPFILE | head -n 5 | tail -n 4); do
		echo -e "\t\t\t\t\t$i"
	done

	#clean up
	rm $TMPFILE
	unset hops
fi


# network benchmark?
	# send packets as fast as possible and time how long it takes
		# (but why? maybe i won't do this.. what does it accomplish?)
	# nmap some stuff maybe? idk

# internet benchmarks?
	#download small pictures over http and https
	#download large files and time it


exit 0
