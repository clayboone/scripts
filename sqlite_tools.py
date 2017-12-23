#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sqlite_tools.py

Accessory functions for working with sqlite3 files and objects in various
scenarios.
"""

import os
import shutil
import tempfile
import sqlite3

from contextlib import contextmanager


@contextmanager
def open_temp_sqlite3(filename, query=None):
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
        raise error

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
