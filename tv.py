#!/usr/bin/env python3

import sys
import requests
from pylgtv import WebOsClient


def main():
    client = WebOsClient('192.168.1.75')
    # client.launch_app('com.webos.app.music')
    # client.launch_app('com.webos.app.home') # not working

    # services = client.get_services()
    # print(services)

    # client.volume_down()
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

    TV_CMD_HOME_MENU = 21  # noqa
    TV_CMD_UP = 12  # noqa
    TV_CMD_DOWN = 13  # noqa
    TV_CMD_LEFT = 14  # noqa
    TV_CMD_RIGHT = 15  # noqa
    TV_CMD_OK = 20  # noqa

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
