#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse and search your web browsing history.

Testing with Chrome 63 and Python 3 on Windows 10

Requirements:
    watchdog >= 0.8.3

Todo:
    * Make a better --follow function. Right now it clears the screen then
    prints n-history entries (default 10) in descending order. I think I'd
    prefer this command to work more like `tail` though.
      - update: we're getting closer to this. now the -f switch makes a
                little more sense, but still clears the screen, and will
                still print out -n entries over and over if i turned the
                screen clearing off. so the status of this is very WIP
"""

import os
import sys
import sqlite3
import tempfile
import shutil
import argparse # click not in stdlib

# from urllib.parse import urlparse
from contextlib import contextmanager
from time import sleep # pylint warns about redefining time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

class FileChangedEventHandler(FileSystemEventHandler):
    """Event handler for dispatching on_modified() when a file is changed."""
    # https://stackoverflow.com/questions/11883336/detect-file-creation-with-watchdog
    def __init__(self, observer, filename, print_history_args):
        """Set this object's oberserver and filename to watch"""
        self.observer = observer
        self.filename = filename
        self.print_history_args = print_history_args
        self.on_modified()

    def on_modified(self, event=None):
        """Dispatched by watchdog.events.FileSystemEventHandler when a file
        in the observer path is modified"""
        # print('event =', event) # uncomment to unleash hell
        if event is None:
            # First run of a --follow comand.  Make sure print_history() is
            # called at least once.
            print_history(self.print_history_args, follow=True)
        else:
            if event.src_path == self.filename:
                print_history(self.print_history_args, follow=True)

class HistoryData(object):
    """Wrapper class for a persistent data object (list of tuples).

    This avoids needing global variables while still keeping a static variable
    as Python doens't really have static variables for functions.
    """
    data = []
    is_first_run = None

    @classmethod
    def __init__(cls, data):
        """Initialize HistoryData.data

        Args:
            data (list): the result of the first time running a query in
            follow mode
        """
        cls.is_first_run = bool(cls.is_first_run is None)
        cls.data = data

    @classmethod
    def get_difference(cls, newdata):
        """Return a list of tuples containing the intersection of our stored
        data and the data passed.

        Args:
            data (list): the result of the most recent database query
        """
        return [row for row in newdata if row not in cls.data]

    @classmethod
    def append_data(cls, newdata):
        """Append newdata (list) to data (list)."""
        cls.data.append(newdata)

def get_chrome_userdata_path():
    """Return this platform's default path to 'User Data' as a string that
    this platform understands. (eg. On Windows,
    'C:\\Users\\username\\App Data\\Local\\Google\\Chrome\\User Data')
    """
    if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        chrome_path_elements = ['Google', 'Chrome', 'User Data']
        return os.path.join(os.getenv('LOCALAPPDATA'), *chrome_path_elements)
    elif sys.platform.startswith('linux'):
        chrome_path_elements = ['.config', 'google-chrome']
        return os.path.join(os.getenv('HOME'), *chrome_path_elements)
    else: # haven't tested 'darwin' or 'java' yet
        sys.exit('Platform \'' + sys.platform + '\' is unsupported')

def print_data_from_tuple(args, data):
    """An accessory function to print_history()

    Print data inside tuple according to args. Data are a list of tuples like:
    ('2017-9-9 13:20:07',
     'hello world - Google Search'
     'https://www.google.com/search?q=hello+world')
    """
    for index, row in enumerate(data):
        if args.all is not True and len(data) - args.count > index:
            continue

        if args.time is True:
            print(row[2], end=': ')

        if len(row[1]) < 1:
            if args.markdown is True:
                print('[No Title]', end='')
            else:
                print('-', end=' ')
                if args.url is not True:
                    # Print the url anyways since title is missing
                    print(row[0], end=' ')
        else:
            if args.markdown is True:
                print('[' + row[1] + ']', end='')
            else:
                print(row[1], end=' ')

        if args.url is True or args.markdown is True:
            print('(' + row[0] + ')')
        else:
            print()

        if args.markdown is True:
            print() # extra line to separate links on the page

def print_history(args, follow=False):
    """Read some rows of a chrome history database.

    Args:
        args (argparse.Namespace): options passed to program.
        follow (bool): were we run from follow mode
    """
    history_filename = os.path.join(
        get_chrome_userdata_path(), args.profile, 'History')

    query_string = (
        'select url, title,'
        'datetime(last_visit_time/1000000-11644473600, "unixepoch")'
        'from urls order by last_visit_time'
    )

    with open_sqlite3(history_filename, query=query_string) as cursor:
        # data = cursor.fetchall()
        data = HistoryData(cursor.fetchall())

    if follow and not data.is_first_run:
        args.all = True
        data = data.get_difference(data)

    print_data_from_tuple(args, data.data)

def list_chrome_profiles():
    """List all sub-directories of the chrome 'User Data' path that contain a
    valid History sqlite3 database and print the profile names to stdout.

    Return: 0 if at least one valid profile was found. 1 otherwise.
    """
    userdata = get_chrome_userdata_path()
    found_valid_profile = False

    # os.listdir() is significantly faster than glob.glob() and has enough
    # functionality for what we need.
    for element in os.listdir(userdata):
        if (os.path.isdir(os.path.join(userdata, element)) and
                os.path.isfile(os.path.join(userdata, element, 'History'))):
                # TODO: fixme somehow.. make pylint and google happy
            # pylint complains about the spacing above.  According to the
            # Google Python Style Guide, this is the correct way and pylint
            # is wrong.
            print(element)
            if not found_valid_profile:
                found_valid_profile = True

    return 0 if found_valid_profile else 1

def main(argv):
    """Program entry point"""
    # Parse command line
    parser = argparse.ArgumentParser(
        description='Inspect your chrome web history')
    parser.add_argument('-l', '--list-profiles',
                        action='store_true', default='False',
                        help='List all chrome profiles for the current user')
    parser.add_argument('-p', '--profile',
                        default='Default',
                        help='the Chrome profile name to inspect')
    parser.add_argument('-t', '--time',
                        action='store_true', default=False,
                        help='Print the time of the history entry')
    parser.add_argument('-u', '--url',
                        action='store_true', default='False',
                        help='Also print the url of the history entry')
    parser.add_argument('-m', '--markdown',
                        action='store_true', default=False,
                        help='Output in Markdown-friendly format')
    parser.add_argument('-f', '--follow',
                        action='store_true', default='False',
                        help='follow profile\'s History file for changes')
    count_group = parser.add_mutually_exclusive_group()
    count_group.add_argument('-n', '--count',
                             type=int, default=10,
                             help='number of entries to show')
    count_group.add_argument('-a', '--all',
                             action='store_true', default=False,
                             help='print all entries in History file')
    args = parser.parse_args(argv[1:])

    # --list-profiles will preempt other functionality
    if args.list_profiles is True:
        return list_chrome_profiles()

    # Read table from database.
    if args.follow is True:
        observer = Observer()
        history_filename = os.path.join(get_chrome_userdata_path(),
                                        args.profile, 'History')
        observer.schedule(
            FileChangedEventHandler(observer, history_filename, args),
            os.path.join(get_chrome_userdata_path(), args.profile)
        )

        # Watch file
        observer.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    else:
        print_history(args)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
