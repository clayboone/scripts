#!/usr/bin/env python3
"""Print the size of the terminal."""

import shutil

if __name__ == '__main__':
    print('{}x{}'.format(*shutil.get_terminal_size()))
