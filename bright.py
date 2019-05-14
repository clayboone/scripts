#!/usr/bin/env python3

import os
import sys
import re
import math
from enum import Enum

BACKLIGHT_PATH = '/sys/class/backlight/intel_backlight'

FILE_BRIGHTNESS = 'brightness'
FILE_MAX_BRIGHTNESS = 'max_brightness'
FILE_ACTUAL_BRIGHTNESS = 'actual_brightness'


class Backlight(object):

    def __init__(self):
        self.__max_brightness = -1
        self.__actual_brightness = -1
        self.__brightness = -1

    @property
    def max_brightness(self):
        with open(os.path.join(BACKLIGHT_PATH, FILE_MAX_BRIGHTNESS)) as fd:
            self.__max_brightness = int(fd.readline().strip())

        return self.__max_brightness

    @property
    def actual_brightness(self):
        with open(os.path.join(BACKLIGHT_PATH, FILE_ACTUAL_BRIGHTNESS)) as fd:
            self.__actual_brightness = int(fd.readline().strip())

        return self.__actual_brightness

    @property
    def brightness(self):
        with open(os.path.join(BACKLIGHT_PATH, FILE_BRIGHTNESS)) as fd:
            self.__brightness = int(fd.readline().strip())

        return self.__brightness

    @brightness.setter
    def brightness(self, value):
        assert isinstance(value, int)
        assert 100 < value <= self.max_brightness

        path = os.path.join(BACKLIGHT_PATH, FILE_BRIGHTNESS)

        try:
            with open(path, 'w') as fd:
                fd.write(f'{value}\n')
        except PermissionError as e:
            print(e, file=sys.stderr)

        return self.brightness


class Action(Enum):
    HELP = 0
    INC_RAW = 1
    DEC_RAW = 2
    INC_PERCENT = 3
    DEC_PERCENT = 4


class CommandLine(object):

    def __init__(self):
        self.action = None

        def shift(x):
            return (x[0], x[1:len(x)])

        self.name, args = shift(sys.argv)

        while len(args) > 0:
            #print(f'shifting {args[0]}')
            arg, args = shift(args)

            if arg == '-h':
                self.action = Action.HELP
                continue

            match = re.search(r'^[+-]\d*%?$', arg)
            print(match)

    def print_usage(self):
        print(f'Usage: {self.name} [-h] {{<[+-]>NUM[%]}}')


def main():
    cli = CommandLine()
    backlight = Backlight()

    if cli.action is None:
        print('{:.0f}%'.format(
            int(backlight.actual_brightness / backlight.max_brightness * 100)
        ))
    elif cli.action is Action.HELP:
        cli.print_usage()
    else:
        print('taking action')

    #backlight.brightness = 4438
    #print(f'actual = {backlight.actual_brightness}')
    #print(f'max = {backlight.max_brightness}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
