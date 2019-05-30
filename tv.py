#!/usr/bin/env python3

import sys
import re
from enum import Enum
from pylgtv import WebOsClient


class Action(Enum):
    HELP = 0
    INC_VOLUME = 1
    DEC_VOLUME = 2
    SET_VOLUME = 3


class TV(object):

    def __init__(self):
        self.client = WebOsClient('192.168.1.75')

    @property
    def volume(self):
        return self.client.get_volume()

    @volume.setter
    def volume(self, value):
        assert isinstance(value, int)
        self.client.set_volume(value)


class CommandLine(object):

    def __init__(self):
        self.action = None
        self.value = None

        def shift(x):
            return (x[0], x[1:len(x)])

        self.progname, args = shift(sys.argv)

        while len(args) > 0:
            arg, args = shift(args)

            if arg == 'volume':

                # search the next arg
                match = re.search(r'^[-+]?\d*$', args[0])

                if match is not None:
                    if match.string[0] == '+':
                        self.action = Action.INC_VOLUME
                    elif match.string[0] == '-':
                        self.action = Action.DEC_VOLUME
                    else:
                        self.action = Action.SET_VOLUME
                        self.value = int(match.string[0:len(match.string)])
                        continue

                    # inc or dec volume
                    self.value = int(match.string[1:len(match.string)])


def main():
    cli = CommandLine()
    tv = TV()

    if cli.action is Action.HELP:
        print('Change the TV volume')
        print('Usage: tv.py volume +1')
    elif cli.action is Action.INC_VOLUME:
        tv.volume += cli.value
    elif cli.action is Action.DEC_VOLUME:
        tv.volume -= cli.value
    elif cli.action is Action.SET_VOLUME:
        tv.volume = cli.value

    #  tv.volume = 0
    #  tv.volume += 2

    #  client = WebOsClient('192.168.1.75')
    # client.launch_app('com.webos.app.music')
    # client.launch_app('com.webos.app.home') # not working

    # services = client.get_services()
    # print(services)

    #  client.volume_down()
    #  print(client.get_volume())
    # client.pause()
    # client.play()

    # client.launch_app('cdp-30')  # plex
    # client.launch_app('earthonline')
    # client.send_enter_key()
    # client.open_url('')

    # client.launch_app('youtube.leanback.v4')
    # client.send_message('good morning amy :D')
    # client.channel_down

    # for app in client.get_apps():
    #    print(app['id'])

    # client.request('audio/volumeUp')
    # client.request('audio/volumeDown')

    # app = client.get_current_app()
    # channel = client.get_current_channel()
    # channel_info = client.get_channel_info()
    # channels = client.get_channels()

    # print(f'app: {app}')
    # print(f'channel: {channel}')
    # print(f'channel_info: {channel_info}')
    # print(f'channels: {channels}')

    # client.open_url('http://asdf.com')
    # c = client.command(
    #     'request',
    #     'http://192.168.1.75:3000/roap/api/command',
    #     21)
    # print(c)

    #  TV_CMD_HOME_MENU = 21  # noqa
    #  TV_CMD_UP = 12  # noqa
    #  TV_CMD_DOWN = 13  # noqa
    #  TV_CMD_LEFT = 14  # noqa
    #  TV_CMD_RIGHT = 15  # noqa
    #  TV_CMD_OK = 20  # noqa

    # a = client.request('media.controls/play')
    # a = client.request('com.webos.service.ime/sendEnterKey')
    # print(a)

    # client.send_enter_key()
    # client.request('tv/HandleKeyInput13')

    #  url = 'http://192.168.1.75:3000/roap/api/command'
    #  headers = {
    #  'Content-Type': 'application/atom+xml'
    #  }
    #  text = '<!--?xml version="1.0" encoding="utf-8" ?--><command></command>' + 'HandleKeyInput21'  # noqa

    #  res = requests.post(url, headers=headers, data=text)
    #  print(res)

    # client.request('system.launcher/open', {
    #     'params': f'{TV_CMD_HOME_MENU}'
    # })

    # res = requests.post('http://192.168.1.75:3000/roap/api/command', {
    #

    # p = '<!--?xml version="1.0" encoding="utf-8" ?--><command></command>' + 'HandleKeyInput21'  # noqa
    # client.request('roap/api/command', p)


if __name__ == '__main__':
    sys.exit(main())
