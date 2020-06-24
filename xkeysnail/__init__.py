# -*- coding: utf-8 -*-


def eval_file(path):
    with open(path, "rb") as file:
        exec(compile(file.read(), path, 'exec'), globals())


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


def cli_main():
    from .info import __logo__, __version__
    print("")
    print(__logo__.strip())
    print("                             v{}".format(__version__))
    print("")

    # Parse args
    import argparse
    from appdirs import user_config_dir
    parser = argparse.ArgumentParser(description='Yet another keyboard remapping tool for X environment.')
    parser.add_argument('config', metavar='config.py', type=str, default=user_config_dir('xkeysnail/config.py'), nargs='?',
                        help='configuration file (See README.md for syntax)')
    parser.add_argument('--devices', dest="devices", metavar='device', type=str, nargs='+',
                        help='keyboard devices to remap (if omitted, xkeysnail choose proper keyboard devices)')
    parser.add_argument('--watch', dest='watch', action='store_true',
                        help='watch keyboard devices plug in ')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='suppress output of key events')
    args = parser.parse_args()

    # Make sure that the /dev/uinput device exists
    if not uinput_device_exists():
        print("""The '/dev/uinput' device does not exist.
Please check your kernel configuration.""")
        import sys
        sys.exit(1)

    # Make sure that user have root privilege
    if not has_access_to_uinput():
        print("""Failed to open `uinput` in write mode.
Make sure that you have executed xkeysnail with root privilege such as

    $ sudo xkeysnail config.py
""")
        import sys
        sys.exit(1)

    # Load configuration file
    eval_file(args.config)

    # Enter event loop
    from xkeysnail.input import loop
    loop(args.devices, args.watch, args.quiet)
