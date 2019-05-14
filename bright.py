#!/usr/bin/env python3

import os
import sys

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


class CommandLine(object):

    def __init__(self):
        def shift(x):
            return x[1:len(x)]

        # Remove script name from args.
        self.args = shift(sys.argv)

        print(self.args)


def main():
    cli = CommandLine()

    if cli.args is None:
        pass

    backlight = Backlight()
    print(backlight.actual_brightness)

    return 0


if __name__ == '__main__':
    sys.exit(main())
