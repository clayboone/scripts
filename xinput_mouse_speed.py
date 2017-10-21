#!/usr/bin/env python3

import gi
import shlex
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class xinput_mouse_speed_window(Gtk.Window):
  
  def __init__(self):
    
    # static (for now) prefixes to commands
    self.__xinput_accel_prefix =  'xinput -set-prop 9 "libinput Accel Speed" '
    self.__xinput_speed_prefix =  'xinput -set-prop 9 '
    self.__xinput_speed_prefix += '"Coordinate Transformation Matrix" '
    self.__xinput_speed_prefix += '1 0 0 0 1 0 0 0 '
    
    # for cancelling/reverting changes later
    self.speed_changed = False
    self.accel_changed = False
    self.initial_speed = self.get_initial_speed()
    self.initial_accel = self.get_initial_accel()
    
    # start making the gui
    Gtk.Window.__init__(self, title="Pointer Speed Frontend for xinput")
    self.set_default_size(400, 200)
    self.set_border_width(5)
    
    # label saying who we are and what we do
    desc  = "eat what you want"
    self.description_label = Gtk.Label()
    self.description_label.set_markup(desc)
    self.description_label.set_line_wrap(True)
    
    self.speed_slider = self.create_slider(min_value=0, max_value=10,
                                           initial_value=self.initial_speed)
    self.speed_slider.connect("button-release-event", self.speed_slider_changed)
    self.speed_slider.connect("key-release-event", self.speed_slider_changed)
    
    self.accel_slider = self.create_slider(min_value=-1, max_value=1,
                                           initial_value=self.initial_accel)
    self.accel_slider.connect("button-release-event", self.accel_slider_changed)
    self.accel_slider.connect("key-release-event", self.accel_slider_changed)
    
    # okay/cancel button box (do i even need buttons??)
    self.button_hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
    
    self.ok_button = Gtk.Button(label="Okay")
    self.ok_button.connect("clicked", self.ok_button_clicked)
    self.button_hbox.pack_end(self.ok_button, True, True, 0)
    
    self.cancel_button = Gtk.Button(label="Cancel")
    self.cancel_button.connect("clicked", self.cancel_button_clicked)
    self.button_hbox.pack_end(self.cancel_button, True, True, 0)
    
    # top level box to contain everything
    self.top_level_vbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
    self.top_level_vbox.pack_start(self.description_label, True, True, 0)
    self.top_level_vbox.pack_start(self.speed_slider, True, True, 0)
    self.top_level_vbox.pack_start(self.accel_slider, True, True, 0)
    self.top_level_vbox.pack_start(self.button_hbox, True, True, 0)
    self.add(self.top_level_vbox)
    
    # ideas for headerbar and/or more widgets:
    #  - a profiles input box/selection menu/listbox (different settings based on game, etc)
    #  - an eventbox? for pressing escape to quit
    #  - a way to choose which device (not everyone's will be the number 9)
  
  def ok_button_clicked(self, widget):
    # no need to run xinput again, just output the command to use for running
    # in some other script (like a startup one)
    try:
      print(self.speed_output_command)
      print(self.accel_output_command)
    except:
      pass
    finally:
      Gtk.main_quit()
  
  def cancel_button_clicked(self, widget):
    # revert to what settings were when opened and exit
    if self.speed_changed:
      cmd_line = self.__xinput_speed_prefix + str(self.initial_speed)
      subprocess.run(shlex.split(cmd_line))
    if self.accel_changed:
      cmd_line = self.__xinput_accel_prefix + str(self.initial_accel)
      subprocess.run(shlex.split(cmd_line))
    Gtk.main_quit() #TODO can i return non-zero here? how?
    
  
  def create_slider(self, initial_value=0, min_value=0, max_value=10, step=0.1, page=0):
    adj = Gtk.Adjustment(initial_value, min_value, max_value, step, page)
    h_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
    h_scale.set_digits(2)
    # because there's apparently a bug in Gtk.Scales where sometimes (about
    # half the time.. ish..) the initial_value won't listen. It sits at 0.0
    if h_scale.get_value() is not initial_value:
      h_scale.set_value(initial_value) # whatever.. >.> hashtag FIXME hashtag foreveralone
    return h_scale
  
  def speed_slider_changed(self, obj, key_or_button):
    speed = round(self.speed_slider.get_value() * -1 + 10, 3)
    cmd_line = self.__xinput_speed_prefix + str(speed)
    subprocess.run(shlex.split(cmd_line))
    self.speed_changed = True
    self.speed_output_command = cmd_line
  
  def accel_slider_changed(self, obj, key_or_button):
    accel = round(self.accel_slider.get_value(), 3)
    cmd_line = self.__xinput_accel_prefix + str(accel)
    subprocess.run(shlex.split(cmd_line))
    self.accel_changed = True
    self.accel_output_command = cmd_line
  
  def get_initial_speed(self):
    cmd_line = "xinput -list-props 9 | grep 'Coordinate Transformation Matrix'"
    output   = subprocess.check_output(cmd_line, shell=True)
    return float(output.split()[-1])
  
  def get_initial_accel(self):
    cmd_line = "xinput -list-props 9 | grep 'libinput Accel Speed'"
    output   = subprocess.check_output(cmd_line, shell=True)
    print(str(round(float(output.split()[-1]), 2)))
    return round(float(output.split()[-1]), 2)

def main():
  win = xinput_mouse_speed_window()
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()

if __name__ == '__main__':
  main()
