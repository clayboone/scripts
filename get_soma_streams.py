#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieve SomaFM stream information."""

import os
import sys
import json
import argparse
import requests


def main(argv):
    """Program entry point when ran."""
    # Parse command line arguments
    # -v = list more stream info (all stream addresses/qualities, not just the
    # highest quality, etc)
    # -s = search? print streams matching regex or something
    # -q = only print stream address, not name/quality/whatever

    # Retrive list of stations/streams
    # after the class is setup, this line should look like:
    # stations = StationList() or something simple stupid

    # Print requested streams
    # for station in stations:
    #   print(station.get_info())
    # or something.. who knows..
    pass

if __name__ == '__main__':
    sys.exit(main(sys.argv))
