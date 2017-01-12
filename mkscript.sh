#!/bin/sh

if [ "$#" -ne 1 ];
then
	echo "Usage: $0 <script_name.sh>"
	exit 1
fi

if [ -f $1 ];
then
	echo "file \"$1\" already exists. Exiting."
	exit 2
fi


# maybe i can use readline to pipe input in, and only use
# this as a fallback if there's is no stdin?
echo "#!/bin/sh" >> $1
chmod +x $1
