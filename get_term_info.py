#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""get_term_info.py

Prints some basic terminal information because Windows doesn't show me the
dimensions of my terminal window when resizing.
"""

import sys
import shutil

def main():
    """Print terminal width and height"""
    width, height = shutil.get_terminal_size()
    print('Terminal size: {}x{}'.format(width, height))

if __name__ == '__main__':
    sys.exit(main())
