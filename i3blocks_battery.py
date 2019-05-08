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


# The example at /usr/lib/i3blocks/battery (perl) prints twice:
# Full text (time remaining based on `acpi`'s estimation and
# Short text (either BAT or CHR)
# Exit with status 33 to signal 'urgent'
#
# The default Perl script also uses the `acpi` command about 3 times per
# instance. That's sorta heavy on resources, and `acpi` isn't installed by
# default and I don't want to install it.
#
# So read files:
# /sys/class/power_supply/BAT0/status   - show's charging state
# /sys/class/power_supply/BAT0/capacity - show's charge level
#
#
# https://superuser.com/questions/808397/understanding-the-output-of-sys-class-power-supply-bat0-uevent
#
# Actually.. it looks like uevent has everything inside of it.. I could just
# read one file once per invocation and do math from there.
#
# charging state = STATUS
# charge level   = ENERGY_NOW / ENERGY_FULL (or CAPACITY)
# time remaining = ENERGY_NOW / POWER_NOW (until discharged)
# ...
# i'll have to figure out how to get time-till-charged

import sys
import os
import glob
import argparse


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Print battery information in one line')
    parser.add_argument('battery_number', type=int, nargs='?')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list available batteries')
    args = parser.parse_args()

    if args.list:
        print_battery_list()
    else:
        if args.battery_number is None:
            parser.print_usage()
            sys.exit(2)
        print(args.battery_number)
