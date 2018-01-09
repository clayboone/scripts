#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieve SomaFM stream information."""

import sys
import argparse
import json
import requests

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
