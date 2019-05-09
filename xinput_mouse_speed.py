#!/usr/bin/env python3

import os
import gi
import shlex
import subprocess
import argparse

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa


class xinput(object):
    """Wrapper class around xinput(1) for X11"""

    DEVICE_ID = '12'
    XINPUT_ACCEL_PREFIX = (
        f'xinput set-prop {DEVICE_ID} "libinput Accel Speed" ')
    XINPUT_SPEED_PREFIX = (
        f'xinput set-prop {DEVICE_ID} "Coordinate Transformation Matrix" '
        '1 0 0 0 1 0 0 0 ')

    def __init__(self):
        self.__device_id = self.device_id()

    def device_id(self):
        """Get the device ID for my Razer Deathadder 2013 mouse.

        The new xinput(1) interface to X11 likes to change the device ID
        whenever the computer sleeps or restarts. So this function grabs it
        dynamically at runtime.
        """
        # TODO: is there a way to use xinput to do this? when the -w file is
        # written, it won't be able to find the device id if it's changed...
        #
        # Or should this program output a small shell script to find the ID
        # at the output script's runtime? ...programs writing programs...

        if self.__device_id is not None:
            return self.__device_id


class Window(Gtk.Window):

    DEVICE_ID = '12'
    XINPUT_ACCEL_PREFIX = (
        f'xinput set-prop {DEVICE_ID} "libinput Accel Speed" ')
    XINPUT_SPEED_PREFIX = (
        f'xinput set-prop {DEVICE_ID} "Coordinate Transformation Matrix" '
        '1 0 0 0 1 0 0 0 ')

    WINDOW_NAME = 'Xinput Config Tool'

    def __init__(self, outfile=None):
        self.speed_changed = False
        self.accel_changed = False
        self.initial_speed = self.get_initial_speed()
        self.initial_accel = self.get_initial_accel()
        self.outfile = outfile

        # Init Gtk.Window
        Gtk.Window.__init__(self, title=self.WINDOW_NAME)
        self.set_default_size(400, 200)
        self.set_border_width(5)

        # Pseudo-title bar
        self.description_label = Gtk.Label()
        self.description_label.set_markup(self.WINDOW_NAME)
        self.description_label.set_line_wrap(True)

        # Sliders
        self.speed_slider = self.create_slider(
            min_value=0, max_value=10, initial_value=self.initial_speed)
        # FIXME: Sometime between Ubuntu 18.04 and Arch 2019-05, this broke.
        # It's always 0.0 on new instances.
        self.speed_slider.connect("button-release-event",
                                  self.speed_slider_changed)
        self.speed_slider.connect("key-release-event",
                                  self.speed_slider_changed)

        self.accel_slider = self.create_slider(
            min_value=-1, max_value=1, initial_value=self.initial_accel)
        self.accel_slider.connect("button-release-event",
                                  self.accel_slider_changed)
        self.accel_slider.connect("key-release-event",
                                  self.accel_slider_changed)

        # Buttons
        self.button_hbox = Gtk.Box(
            spacing=10, orientation=Gtk.Orientation.HORIZONTAL)

        self.ok_button = Gtk.Button(label="Okay")
        self.ok_button.connect("clicked", self.ok_button_clicked)
        self.button_hbox.pack_end(self.ok_button, True, True, 0)

        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.connect("clicked", self.cancel_button_clicked)
        self.button_hbox.pack_end(self.cancel_button, True, True, 0)

        # Container
        self.top_level_vbox = Gtk.Box(
            spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.top_level_vbox.pack_start(self.description_label, True, True, 0)
        self.top_level_vbox.pack_start(self.speed_slider, True, True, 0)
        self.top_level_vbox.pack_start(self.accel_slider, True, True, 0)
        self.top_level_vbox.pack_start(self.button_hbox, True, True, 0)
        self.add(self.top_level_vbox)

    def ok_button_clicked(self, widget):
        # No need to run xinput again
        # Print the xinput commands required to get this configuration again
        if self.outfile is not None:
            try:
                with open(self.outfile, 'w') as fd:
                    fd.write('#!/bin/sh\n')
                    fd.write('{}\n'.format(self.speed_output_command))
                    fd.write('{}\n'.format(self.accel_output_command))

                os.chmod(self.outfile, 0o744)
            except BaseException:
                if __debug__:
                    print(f'Open {self.outfile} failed or one of the vars did')
        else:
            try:
                print(self.speed_output_command)
                print(self.accel_output_command)
            except BaseException:
                if __debug__:
                    print(f'One of the vars is not set')

        Gtk.main_quit()

    def cancel_button_clicked(self, widget):
        # Revert changes and exit
        if self.speed_changed:
            cmd_line = self.XINPUT_SPEED_PREFIX + str(self.initial_speed)
            subprocess.run(shlex.split(cmd_line))
        if self.accel_changed:
            cmd_line = self.XINPUT_ACCEL_PREFIX + str(self.initial_accel)
            subprocess.run(shlex.split(cmd_line))
        Gtk.main_quit()

    def create_slider(self, initial_value=0, min_value=0,
                      max_value=10, step=0.1, page=0):
        adj = Gtk.Adjustment(value=initial_value,
                             lower=min_value,
                             upper=max_value,
                             step_increment=step,
                             page_increment=page)
        h_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                            adjustment=adj)

        h_scale.set_digits(2)
        h_scale.set_value(initial_value)

        return h_scale

    def speed_slider_changed(self, obj, key_or_button):
        speed = round(self.speed_slider.get_value() * -1 + 10, 3)
        cmd_line = self.XINPUT_SPEED_PREFIX + str(speed)
        subprocess.run(shlex.split(cmd_line))
        self.speed_changed = True
        self.speed_output_command = cmd_line

    def accel_slider_changed(self, obj, key_or_button):
        accel = round(self.accel_slider.get_value(), 3)
        cmd_line = self.XINPUT_ACCEL_PREFIX + str(accel)
        subprocess.run(shlex.split(cmd_line))
        self.accel_changed = True
        self.accel_output_command = cmd_line

    def get_initial_speed(self):
        cmd = f"xinput list-props {self.DEVICE_ID} | grep 'Coordinate Transformation Matrix'"
        output = subprocess.check_output(cmd, shell=True)

        if __debug__:
            print(f'Initial speed: {float(output.split()[-1])}')

        return float(output.split()[-1])

    def get_initial_accel(self):
        # xinput prints 2 lines matching this now...
        cmd = f"xinput list-props {self.DEVICE_ID} | grep 'libinput Accel Speed (293)'"
        output = subprocess.check_output(cmd, shell=True)

        if __debug__:
            print(f'Initial Accel {round(float(output.split()[-1]), 2)}')

        return round(float(output.split()[-1]), 2)


def main():
    parser = argparse.ArgumentParser(
        description='Frontend for xinput (device ID 18)')
    parser.add_argument('-w', '--write-file', type=str, nargs=1,
                        help='create script automatically')
    args = parser.parse_args()

    if args.write_file is not None:
        win = Window(outfile=args.write_file[0])
    else:
        win = Window()

    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
