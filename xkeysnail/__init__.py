def eval_file(path):
    with open(path, "rb") as file:
        exec(compile(file.read(), path, 'exec'))


def has_access_to_uinput():
    from evdev.uinput import UInputError
    try:
        from xkeysnail.output import _uinput
        return True
    except UInputError as ex:
        return False


def cli_main():
    from .info import __logo__, __version__
    print("")
    print(__logo__.strip())
    print("                             v{}".format(__version__))
    print("")

    # Parse args
    import argparse
    parser = argparse.ArgumentParser(description='Yet another keyboard remapping tool for X environment.')
    parser.add_argument('config', metavar='config.py', type=str,
                        help='configuration file (See README.md for syntax)')
    parser.add_argument('--devices', dest="devices", metavar='device', type=str, nargs='+',
                        help='keyboard devices to remap (if omitted, xkeysnail choose proper keyboard devices)')
    args = parser.parse_args()

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
    from xkeysnail.input import loop, select_device
    loop(select_device(args.devices))
