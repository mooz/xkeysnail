# -*- coding: utf-8 -*-
import os
import sys


def eval_file(path, startup_delay):
    if startup_delay:
        from time import sleep
        print('Startup delay enable, wait for %s' % startup_delay)
        sleep(startup_delay)

    try:
        with open(path, "rb") as file:
            exec(compile(file.read(), path, 'exec'), globals())
    except (FileNotFoundError, TypeError):
        print('Config.py not found, use --config or place config.py in %s' % path)
        exit(1)


def uinput_device_exists():
    from os.path import exists
    return exists('/dev/uinput')


def has_access_to_uinput():
    from evdev.uinput import UInputError
    try:
        from xkeysnail.output import _uinput  # noqa: F401
        return True
    except UInputError:
        return False


def cli_main(config_file, args):
    from .info import __logo__, __version__
    # Load configuration file
    eval_file(config_file, args.boot)
    print("")
    print(__logo__.strip())
    print("                             v{}".format(__version__))
    print("")
    # Make sure that the /dev/uinput device exists
    if not uinput_device_exists():
        print("""The '/dev/uinput' device does not exist.
Please check your kernel configuration.""")
        sys.exit(1)

    # Make sure that user have root privilege
    if not has_access_to_uinput() or os.getuid() != 0:
        print("""Failed to open `uinput` in write mode.
Make sure that you have executed xkeysnail with root privilege such as

    $ sudo xkeysnail config.py
""")
        sys.exit(1)

    # Enter event loop
    from xkeysnail.input import loop
    loop(args.devices, args.watch, args.quiet)
