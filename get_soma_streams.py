#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieve SomaFM stream information.

The only sort of API SomaFM gave me was a JSON file location containing info
about the streams they host across a couple of servers.

The JSON file contains a single array called "channels" which holds about 32
channels. Each channel has a single-word "id" value, a title, description,
genre, URLs for artwork (image, largeimage, and xlimage), the number of active
listeners, the last song (current song?) [being] played, and the actual stream
locations.

The stream URLs in each channel are *.pls files and the array in each channel
is called "playlists". They're sorted according to quality.

Opening any *.pls file, there are two entries in a sort of *.ini format. Each
entry contains a file name (ie. the URL), a more verbose title, and a song
length (always -1).

===============================================================================
Example of channels.json (only the top entry is shown for brevity):
{"channels": [
	{
		"id": "7soul",
		"title": "Seven Inch Soul",
		"description": "Vintage soul tracks from the original 45 RPM vinyl.",
		"dj": "Dion Watts Garcia",
		"djmail": "dion@somafm.com",
		"genre": "oldies",
		"image": "https://api.somafm.com/img/7soul120.png",
		"largeimage": "https://api.somafm.com/logos/256/7soul256.png",
		"xlimage": "https://api.somafm.com/logos/512/7soul512.png",
		"twitter": "SevenInchSoul",
		"updated": "1396144686",
		"playlists": [
			{ "url": "https://api.somafm.com/7soul130.pls", "format": "aac",  "quality": "highest" },
			{ "url": "https://api.somafm.com/7soul.pls", "format": "mp3",  "quality": "high" },
			{ "url": "https://api.somafm.com/7soul64.pls", "format": "aacp",  "quality": "high" },
			{ "url": "https://api.somafm.com/7soul32.pls", "format": "aacp",  "quality": "low" }
		],
		"listeners": "68",
		"lastPlaying": "The Capitols - Don't Say Maybe Baby"
	},
}

Example of playlist contents (https://api.somafm.com/7soul130.pls)
[playlist]
numberofentries=2
File1=http://ice1.somafm.com/7soul-128-aac
Title1=SomaFM: Seven Inch Soul (#1  ): Vintage soul tracks from the original 45 RPM vinyl.
Length1=-1
File2=http://ice3.somafm.com/7soul-128-aac
Title2=SomaFM: Seven Inch Soul (#2  ): Vintage soul tracks from the original 45 RPM vinyl.
Length2=-1
Version=2
"""

import sys
import argparse
import json
import requests

class SomaChannel(object):
    def __init__(self):
        pass

class SomaChannelList(dict):
    """A list of SomaFM channels."""
    def __init__(self):
        pass

    def __repr__(self):
        pass

def main(argv):
    """Program entry point when ran."""
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search', nargs=1)
    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument('-v', '--verbose', action='store_true',
                               default=False, help='Print more information')
    verbose_group.add_argument('-q', '--quiet', action='store_true',
                               default=False, help='Only print stream address')
    args = parser.parse_args(argv)

    # Retrive list of stations/streams
    # after the class is setup, this line should look like:
    # stations = StationList() or something simple stupid

    # Print requested streams
    # for station in stations:
    #   print(station.get_info())
    # or something.. who knows..

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
