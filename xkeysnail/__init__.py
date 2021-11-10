#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""init xkeysnail module."""

__version__ = '0.4.81'
__logo__ = """
██╗  ██╗██╗  ██╗███████╗██╗   ██╗
╚██╗██╔╝██║ ██╔╝██╔════╝╚██╗ ██╔╝
 ╚███╔╝ █████╔╝ █████╗   ╚████╔╝
 ██╔██╗ ██╔═██╗ ██╔══╝    ╚██╔╝
██╔╝ ██╗██║  ██╗███████╗   ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝
  ███████╗███╗   ██╗ █████╗ ██╗██╗
  ██╔════╝████╗  ██║██╔══██╗██║██║
  ███████╗██╔██╗ ██║███████║██║██║
  ╚════██║██║╚██╗██║██╔══██║██║██║
  ███████║██║ ╚████║██║  ██║██║███████╗
  ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚══════╝
"""

import os
import sys
import argparse

from time import sleep
from os.path import join
from os.path import exists


parser = argparse.ArgumentParser(
    description='Yet another keyboard remapping tool for X environment.')
parser.add_argument(
    '-c', '--config', dest="config",
    metavar='config.py', type=str, nargs='?',
    help='configuration file (See README.md for syntax)')
parser.add_argument(
    '-d', '--devices', dest="devices",
    metavar='device', type=str, nargs='+',
    help='keyboard devices to remap (if omitted, xkeysnail choose proper keyboard devices)')
parser.add_argument(
    '-w', '--watch', dest='watch',
    action='store_true',
    help='watch keyboard devices plug in ')
parser.add_argument(
    '-q', '--quiet', dest='quiet',
    action='store_true',
    help='suppress output of key events')
parser.add_argument(
    '-b', '--boot', dest='boot',
    metavar='boot', type=int, default=1,
    help='startup delay to wait config file with systemd')
parser.add_argument(
    '-k', '--kill', dest='kill',
    action='store_true',
    help='kill other xkeysnail instancies')

argments = parser.parse_args()

DEVICE = argments.devices
WATCH  = argments.watch
QUIET = argments.quiet
BOOT = argments.boot
KILL = argments.kill


def search_for_configdir(args_path, wait_time):
    """Method to search config diretory."""
    founded_msg = "\nConfig diretory founded: %s"
    USERHOME = os.path.expanduser('~').replace(
        '/root', '/home/%s' % os.environ.get('SUDO_USER'))
    POSSIBLE_CONFIG_DIRS = [args_path] if args_path else [
        join(USERHOME, _path) for _path in [
            '.xkeysnail/',
            '.config/xkeysnail/'
        ]
    ]
    if args_path:
        if exists(args_path):
            print(founded_msg % args_path)
            return args_path

    if wait_time > 1:
        print('\nStartup delay enable, wait for %s' % wait_time)
    for _ in range(wait_time):
        for item in POSSIBLE_CONFIG_DIRS:
            if os.path.exists(item):
                print(founded_msg % item)
                return item
        sleep(1)
    print('\nConfig directory not found:')
    print(' Create the "%s" directory and place the "config.py" file inside it.' %
            ', '.join(POSSIBLE_CONFIG_DIRS))
    sys.exit(0)

CONFIG = search_for_configdir(argments.config, BOOT)
