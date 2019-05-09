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
import argparse
from datetime import timedelta as delta


POWER_SUPPLY_PATH = '/sys/class/power_supply'
UEVENT_FILENAME = 'uevent'


def print_battery_list():
    # Header
    print('NUM\tCharge\tModel')

    for path in glob.glob(os.path.join(POWER_SUPPLY_PATH, 'BAT*')):
        with open(os.path.join(path, UEVENT_FILENAME), 'r') as fd:
            for line in [line.strip() for line in fd.readlines()]:
                name, value = line.split('=')
                name = name.lower()[len('POWER_SUPPLY_'):]

                if name == 'name':
                    bat_num = value[3:]
                elif name == 'capacity':
                    capacity = value
                elif name == 'model_name':
                    model = value
                elif name == 'manufacturer':
                    make = value
                else:
                    continue

        print(f'{bat_num}\t{capacity}%\t{make} {model}')


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Print battery information in one line')
    parser.add_argument('battery_number', type=int, nargs='?')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list available batteries and exit')
    parser.add_argument('-p', '--precision', type=int, default=0,
                        help='precision of percentage output')
    args = parser.parse_args()

    if args.list:
        print_battery_list()
    else:
        # Quit if we don't have a battery number; No defaults
        if args.battery_number is None:
            parser.print_usage()
            sys.exit(2)

        # Get information for selected battery
        info = get_battery_info(args.battery_number)

        # Get format string for chosen precision
        if args.precision <= 0:
            fmt_str = '{}{:.0f}% [{}]'
        else:
            fmt_str = '{}{:.' + str(args.precision) + 'f}% [{}]'

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
        print(out)  # Long form
        print(out)  # Short form
        print('#a1a1a1')  # Foreground color
        print('#00a000')  # Background color (why isn't this working?)

        # Magic exit code to make the background solid red.
        if int(info['capacity']) <= 15:
            sys.exit(33)
