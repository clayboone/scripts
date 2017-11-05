#!/usr/bin/env python3

import argparse
import socket

def is_port_up(host, port):
  """included in a loop, return bool"""
  ret = False
  ss = socket.socket()
  ss.settimeout(0.4)
  try:
    ss.connect((host, port))
    ret = True
  finally:
    ss.close()
    return ret

def lookup(hosts=None, ports=None):
  if hosts is not None:
    for host in hosts:
      open_ports = []
      try:
        result = socket.gethostbyname(host)
        if ports is not None:
          for port in ports:
            if is_port_up(result, port) == True:
              open_ports.append(str(port))
      except socket.gaierror:
        result = "No DNS A record found."
      print('{} = {}'.format(host, result), end=' ')
      if len(open_ports) > 0:
        for port in open_ports:
          print('[{}]'.format(port), end=' ')
      print()

if __name__ == '__main__':
  with open('hosts_to_scan.txt', 'r') as f:
    #todo: read file into hosts[]
    pass

  tcp_ports = [21, 22, 23, 80, 8080, 8090, 443, 25565]
  if len(hosts) > 1:
    lookup(hosts, tcp_ports)
  else:
    print("No hosts specified.")
