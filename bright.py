#!/usr/bin/env python3

import os
import sys
import re
import gi
from enum import Enum

gi.require_version('Notify', '0.7')
from gi.repository import Notify  # noqa

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
        path = os.path.join(BACKLIGHT_PATH, FILE_BRIGHTNESS)

        if value < 100:
            value = 100
        if value > self.max_brightness:
            value = self.max_brightness

        try:
            with open(path, 'w') as fd:
                fd.write(f'{value}\n')
        except PermissionError as e:
            print(e, file=sys.stderr)

        return self.brightness


class Notifier(object):

    @staticmethod
    def send_notification(string):
        Notify.init('bright.py')
        notification = Notify.Notification.new('Brightness', string)
        notification.show()


class Action(Enum):
    HELP = 0
    INC_RAW = 1
    DEC_RAW = 2
    INC_PERCENT = 3
    DEC_PERCENT = 4


class CommandLine(object):

    def __init__(self):
        self.action = None
        self.value = None
        self.should_notify = True

        def shift(x):
            return (x[0], x[1:len(x)])

        self.name, args = shift(sys.argv)

        while len(args) > 0:
            arg, args = shift(args)

            if arg == '-h':
                self.action = Action.HELP
                continue

            if arg == '-q':
                self.should_notify = False
                continue

            match = re.search(r'^[+-]\d*%?$', arg)
            if match is not None:
                s = match.string
                if s[0] == '+':
                    if s[len(s)-1] == '%':
                        self.action = Action.INC_PERCENT
                        self.value = abs(int(s[1:len(s)-1]))
                    else:
                        self.action = Action.INC_RAW
                        self.value = abs(int(s[1:]))

                if s[0] == '-':
                    if s[len(s)-1] == '%':
                        self.action = Action.DEC_PERCENT
                        self.value = abs(int(s[1:len(s)-1]))
                    else:
                        self.action = Action.DEC_RAW
                        self.value = abs(int(s[1:]))

    def print_usage(self):
        print(f'Usage: {self.name} [-h] [-q] {{<[+-]>NUM[%]}}')


def main():
    cli = CommandLine()
    backlight = Backlight()
    initial_brightness = backlight.actual_brightness

    def percent(val):
        return int(backlight.max_brightness * val / 100)

    if cli.action is None:
        print('{:.0f}%'.format(
            int(backlight.actual_brightness / backlight.max_brightness * 100)
        ))
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

    if backlight.actual_brightness != initial_brightness and cli.should_notify:
        Notifier.send_notification('{:.0f}%'.format(
            backlight.actual_brightness / backlight.max_brightness * 100))

    return 0


if __name__ == '__main__':
    sys.exit(main())
