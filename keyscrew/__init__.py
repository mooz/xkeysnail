#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""init keyscrew module."""

__version__ = '0.4.81'
__logo__ = """
██╗   ██╗                              █████████╗
██║  ██╔╝                             ██╔═══════╝
██║ ██╔╝  ███████╗ ██╗   ██╗ ███████╗ ██║         ███████╗  ███████╗ ██╗ ██╗ ██╗
█████╗    ██╔════╝ ╚██╗ ██╔╝ ██╔════╝ ██║         ██╔═══██╗ ██╔════╝ ██║ ██║ ██║
██╔═██╗   █████╗    ╚████╔╝  ███████╗ ██║         ██████║═╝ █████╗   ██║ ██║ ██║
██║  ██╗  ██╔══╝     ╚██╔╝   ╚════██║ ██║         ██╔══██╗  ██╔══╝   ██║ ██║ ██╝
██║   ██╗ ███████╗    ██║    ███████║  █████████╗ ██║   ██╗ ███████╗   ██████╗╝
╚═╝   ╚═╝ ╚══════╝    ╚═╝    ╚══════╝  ╚════════╝ ╚═╝   ╚═╝ ╚══════╝    ╚════╝
"""

import os
import sys
import argparse

from time import sleep
from os.path import join, exists

parser = argparse.ArgumentParser(
    description="Keyboard remapping tool.")
parser.add_argument(
    "-c",
    "--config",
    dest="config",
    metavar="config.py",
    type=str,
    nargs="?",
    help="configuration file (See README.md for syntax)"
)
parser.add_argument(
    "-d",
    "--devices",
    dest="devices",
    metavar="device",
    type=str,
    nargs="+",
    help="keyboard devices to remap (if omitted, keyscrew choose proper keyboard devices)"
)
parser.add_argument(
    "-w",
    "--watch",
    dest="watch",
    action="store_true",
    help="watch keyboard devices plug in "
)
parser.add_argument(
    "-q",
    "--quiet",
    dest="quiet",
    action="store_true",
    help="suppress output of key events"
)
parser.add_argument(
    "-b",
    "--boot",
    dest="boot",
    metavar="boot",
    type=int,
    default=1,
    help="startup delay to wait config file with systemd"
)
parser.add_argument(
    "-k",
    "--kill",
    dest="kill",
    action="store_true",
    help="kill other keyscrew instancies"
)

argments = parser.parse_args()

DEVICE = argments.devices
WATCH  = argments.watch
QUIET = argments.quiet
BOOT = argments.boot
KILL = argments.kill


def search_for_configdir(args_path, wait_time):
    """Method to search config diretory."""

    userhome = os.path.expanduser('~')

    if "root" in userhome:
        userhome = userhome.replace(
            "/root",
            f"/home/{os.environ.get('SUDO_USER')}"
        )

    possible_config_dirs = list(map(
        lambda x: join(userhome, x),
        [".keyscrew/",".config/keyscrew/"]
    ))

    try:
        if exists(args_path):
            print(f"\nConfig diretory founded: {args_path}")
            return args_path
    except TypeError:
        pass

    if wait_time > 1:
        print(f"\nStartup delay enable, wait for {wait_time}")

    for _ in range(wait_time):
        for item in possible_config_dirs:
            if exists(item):
                print(f"\nConfig diretory founded: {item}")
                return item
        sleep(1)
    print("\nConfig directory not found:")
    print(
        f" Create the `{' or '.join(possible_config_dirs)}`",
        "directory and place the `config.py` file inside it."
    )
    sys.exit(0)

CONFIG = search_for_configdir(argments.config, BOOT)
