#!/usr/bin/env python3
"""Program to set the brightness of the LVDS backlight on Intel laptops."""

import re
import sys
from enum import Enum
from pathlib import Path

# pylint: disable=missing-docstring


class Backlight():
    """Backlight object representing /sys/class/backlight on Intel devices."""

    SYS_BACKLIGHT_DIR = Path('/sys/class/backlight/intel_backlight')
    BRIGHTNESS_FILE = SYS_BACKLIGHT_DIR / 'brightness'
    MAX_BRIGHTNESS_FILE = SYS_BACKLIGHT_DIR / 'max_brightness'
    ACTUAL_BRIGHTNESS_FILE = SYS_BACKLIGHT_DIR / 'actual_brightness'

    @property
    def max_brightness(self):
        return int(self.MAX_BRIGHTNESS_FILE.read_text())

    @property
    def actual_brightness(self):
        return int(self.ACTUAL_BRIGHTNESS_FILE.read_text())

    @property
    def brightness(self):
        return int(self.BRIGHTNESS_FILE.read_text())

    @brightness.setter
    def brightness(self, value):
        assert isinstance(value, int)

        if value < 100:
            value = 100
        if value > self.max_brightness:
            value = self.max_brightness

        self.BRIGHTNESS_FILE.write_text(f'{value}\n')

        return value


class Action(Enum):
    HELP = 0
    INC_RAW = 1
    DEC_RAW = 2
    SET_RAW = 3
    INC_PERCENT = 4
    DEC_PERCENT = 5
    SET_PERCENT = 6


class CommandLine():
    def __init__(self):
        self.action = None
        self.value = None

        def shift(queue):
            return (queue[0], queue[1:])

        self.name, args = shift(sys.argv)

        while args:
            arg, args = shift(args)

            if arg == '-h':
                self.action = Action.HELP
                continue

            match = re.search(r'^[+-]?\d*%?$', arg)
            if match is not None:
                match = match.string
                if match[0] == '+':
                    if match[-1] == '%':
                        self.action = Action.INC_PERCENT
                        self.value = abs(int(match[1:-1]))
                    else:
                        self.action = Action.INC_RAW
                        self.value = abs(int(match[1:]))

                    continue

                if match[0] == '-':
                    if match[-1] == '%':
                        self.action = Action.DEC_PERCENT
                        self.value = abs(int(match[1:-1]))
                    else:
                        self.action = Action.DEC_RAW
                        self.value = abs(int(match[1:]))

                    continue

                if match[-1] == '%':
                    self.action = Action.SET_PERCENT
                    self.value = int(match[:-1])
                else:
                    self.action = Action.SET_RAW
                    self.value = int(match)

    def print_usage(self):
        print(f'Usage: {self.name} [-h] {{<[+-]>NUM[%]}}')


def main():
    cli = CommandLine()
    backlight = Backlight()

    def percent(val):
        return int(backlight.max_brightness * val / 100)

    if cli.action is None:
        print('{:.0f}%'.format(
            int(backlight.actual_brightness / backlight.max_brightness * 100)))
    elif cli.action is Action.HELP:
        cli.print_usage()
    elif cli.action is Action.INC_PERCENT:
        backlight.brightness += percent(cli.value)
    elif cli.action is Action.INC_RAW:
        backlight.brightness += cli.value
    elif cli.action is Action.DEC_PERCENT:
        backlight.brightness -= percent(cli.value)
    elif cli.action is Action.DEC_RAW:
        backlight.brightness -= cli.value
    elif cli.action is Action.SET_PERCENT:
        backlight.brightness = percent(cli.value)
    elif cli.action is Action.SET_RAW:
        backlight.brightness = cli.value


if __name__ == '__main__':
    main()
