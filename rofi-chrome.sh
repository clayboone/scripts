#!/bin/sh
# Copyright Whatever 2018 Tener
# Officially my first addition to this repo for FreeBSD :)

x=`cat <<EOF | rofi -dmenu -i -p "Chrome: "
GMail
Google Inbox
Google Calendar
Google Keep
Reddit
EOF
`

case "$x" in
	"GMail")
		exec chrome "https://gmail.com"
		break
		;;
	"Google Inbox")
		exec chrome "https://inbox.google.com"
		break
		;;
	"Google Calendar")
		exec chrome "https://calendar.google.com"
		break
		;;
	"Reddit")
		exec chrome "https://reddit.com"
		break
		;;
	"Google Keep")
		exec chrome "https://keep.google.com"
		break
		;;
	*)
		# just search (for now)
		[ -z "$x" ] || exec chrome "https://google.com/search?q=$x"
esac

