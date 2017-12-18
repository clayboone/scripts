#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse and search your web browsing history.

Testing with Chrome 63 and Python 3 on Windows 10

Requirements:
    watchdog >= 0.8.3 # note implemented yet
    pandas >= 0.21.0 # not implemented yet

Note: The requirements are totally optional. The program is made to run using
only the standard library.
"""

import os
import sys
import sqlite3
import tempfile
import shutil
import argparse # click not in stdlib

# from urllib.parse import urlparse
from contextlib import contextmanager

@contextmanager
def open_sqlite3(filename, query=None):
    """Context manager for reading an sqlite3 database while it's in use.

    Args:
        filename (str): The filename of the databse which we want to open
        query (str): The query to run on that databse (optional)

    Yield:
        if query is None:
            A connection object on which the caller can run queries and
            manage cursors themselves.
        else:
            A cursor object with the result of query.
    """
    # "Open..."
    tmp_filepath = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_filepath, os.path.basename(filename))

    try:
        shutil.copyfile(filename, tmp_filename)
    except (IOError, shutil.SameFileError) as error:
        # Consider this unrecoverable for now.
        shutil.rmtree(tmp_filepath)
        sys.exit(error)

    connection = sqlite3.connect(tmp_filename)

    # "Yield..."
    if query is None:
        yield connection
    else:
        cursor = connection.execute(query)
        yield cursor

    # "Close..."
    connection.close()
    shutil.rmtree(tmp_filepath)

def print_history(profile_name, num_rows, outfile=sys.stdout):
    """Read some rows of a chrome history database"""
    history_filename = os.path.join(
        os.getenv('LOCALAPPDATA'),
        *['Google', 'Chrome', 'User Data', profile_name, 'History'])

    query_string = ('select datetime(last_visit_time/1000000-11644473600,'
                    '"unixepoch"), url from urls order by last_visit_time desc')

    with open_sqlite3(history_filename, query=query_string) as cursor:
        # ('2018-9-29 15:24:7', 'https://www.google.com/search?q=hi+mom')
        for index, row in enumerate(cursor):
            if index > num_rows - 1:
                break
            time, data = row
            print(time, data, file=outfile)

def main():
    """Program entry point"""
    # Parse command line
    parser = argparse.ArgumentParser(
        description='Inspect your chrome web history')
    parser.add_argument('-w', '--watch', action='store_true', default='False',
                        help='Watch file in real-time')
    parser.add_argument('-p', '--profile', default='Default',
                        help='the Chrome profile name to inspect')
    parser.add_argument('-n', '--count', type=int, default=10,
                        help='number of entries to show')
    args = parser.parse_args()

    # Read table from database.
    print_history(args.profile, args.count)

if __name__ == '__main__':
    sys.exit(main())
