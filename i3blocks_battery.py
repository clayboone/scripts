#!/usr/bin/env python3
"""i3blocks_battery.py
A replacement for the Perl script that ships with i3blocks to monitor battery
status.

The default script uses acpi(1) which modern distro's don't package by default
anymore. They do typically use the newer /sys tmpfs, and battery information
should be in there.

Additionally, sometimes the acpi(1) output for battery percentage and time
remaining can be very, very wrong ("135%" full charge, shutdown at %60, etc)
"""


import sys
import os
import glob
from argparse import ArgumentParser
from datetime import timedelta as delta


POWER_SUPPLY_PATH = '/sys/class/power_supply'
UEVENT_FILENAME = 'uevent'


def print_battery_list():
    # Header
    print('NUM\tCharge\tCapacity\tModel')

    # For each battery
    for path in glob.glob(os.path.join(POWER_SUPPLY_PATH, 'BAT*')):
        with open(os.path.join(path, UEVENT_FILENAME), 'r') as fd:
            for line in [line.strip() for line in fd.readlines()]:
                name, value = line.split('=')
                name = name.lower()[len('POWER_SUPPLY_'):]

                if name == 'name':
                    bat_num = value[3:]
                elif name == 'capacity':
                    capacity = value
                elif name == 'energy_full_design':
                    # The file is in microampere hours. Unit conversion to
                    # milliampere hours is x / 1,000, but eBay lists these
                    # batteries as x / 10,000. Who to believe?
                    storage = '{:,}mAh'.format(int(value) // 1000)
                elif name == 'model_name':
                    model = value
                elif name == 'manufacturer':
                    make = value
                else:
                    continue

        # Print relevant information
        print(f'{bat_num}\t{capacity}%\t{storage}\t{make} {model}')


def get_battery_info(battery_number):
    # Read the battery's uevent file
    with open(os.path.join(POWER_SUPPLY_PATH,
                           f'BAT{battery_number}',
                           UEVENT_FILENAME),
              'r') as fd:
        lines = fd.readlines()

    # Return a dict out of the values
    b = {}
    for k, v in [l.split('=') for l in [line.strip() for line in lines]]:
        b[k.lower()[len('POWER_SUPPLY_'):]] = v

    return b


class CommandLine(object):
    """Process the command line arguments sent to the program."""

    def __init__(self):
        """Parse args immediately."""
        self.parser = ArgumentParser(
            description='i3blocks-style battery information')

        # optional args
        self.parser.add_argument(
            '-i', '--instance', type=int, default=None,
            help='battery number (same as"instance=0" in i3blocks.conf)')
        self.parser.add_argument(
            '-l', '--list', action='store_true',
            help='list available batteries and exit')
        self.parser.add_argument(
            '-d', '--decimals', type=int, default=0,
            help='precision of percentage output in decimal numbers')
        self.parser.add_argument(
            '-p', '---pango', action='store_true',
            help='output in pango format')
        self.parser.add_argument(
            '-c', '--critical-level', type=int, default=5,
            help='precision of percentage output')
        self.parser.add_argument(
            '-fg', '--fg-color', type=str, default='#FFFFFF',
            help='foreground color as HTML color code')
        self.args = self.parser.parse_args()

    def usage(self):
        """Print usage information."""
        self.parser.print_usage()

    def error(self, msg):
        self.parser.error(msg)


def main():
    cli = CommandLine()
    err = None

    if cli.args.list:
        print_battery_list()
        sys.exit(0)

    # Find a battery number from somewhere or else quit.
    if cli.args.instance is not None:
        battery_number = cli.args.instance
    elif os.getenv('BLOCK_INSTANCE') is not None:
        try:
            battery_number = int(os.getenv('BLOCK_INSTANCE'))
        except ValueError:
            err = 'BLOCK_INSTANCE variable must be an integer'
            cli.error(err)
    else:
        cli.usage()
        sys.exit(2)

    # Get information for selected battery
    info = get_battery_info(battery_number)

    # Get format string for chosen precision
    if cli.args.decimals <= 0:
        fmt_str = '{}{:.0f}% [{}]'
    else:
        fmt_str = '{}{:.' + str(cli.args.decimals) + 'f}% [{}]'

    # Get time-till-charged
    # The status can also be "Unknown" in case the battery is full, but
    # still plugged in. So we check only whether or not it's discharging.
    if 'discharging' in info['status'].lower():
        time_str = ':'.join(str(
            delta(int(info['energy_now']) / int(info['power_now']) / 24)
        ).split(':')[:2])
    else:
        time_str = '--:--'

    # Generate output
    out = fmt_str.format(
        '⚡ ' if 'discharging' in info['status'].lower() else '⏚  ',
        int(info['energy_now']) / int(info['energy_full']) * 100,
        time_str
    )

    # Print stuff
    if os.getenv('BLOCK_MARKUP') == 'pango' or cli.args.pango:
        if err:
            print(err, file=sys.stderr)
        else:
            print('<span background="red">hello</span>')
    else:
        print(out)  # Long form
        print(out)  # Short form
        print(cli.args.fg_color)  # Foreground color

    # Magic exit code to make the background solid red.
    if int(info['capacity']) <= cli.args.critical_level:
        sys.exit(33)


if __name__ == '__main__':
    sys.exit(main())
