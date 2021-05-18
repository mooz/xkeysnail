# -*- coding: utf-8 -*-
import os
import sys
import signal
from os.path import join


def current_pid():
    from os import getpid
    return getpid()

def has_another_instace(lockfile):
    if os.path.isfile(lockfile):
        return True

def startup_lock(lockfile, pid):
    try:
        lockfile = open(lockfile, 'w+')
        lockfile.write(str(pid))
    finally:
        lockfile.close()

def config_dir_search(path):
    USERHOME = os.path.expanduser('~').replace(
        '/root', '/home/%s' % os.environ.get('SUDO_USER'))
    POSSIBLE_CONFIG_DIRS = [
        join(USERHOME, path) for path in [
            '.xkeysnail/',
            '.config/xkeysnail/'
        ]
    ]
    if not path:
        for filepath in POSSIBLE_CONFIG_DIRS:
            if os.path.isdir(filepath):
                return filepath
        return ', '.join(POSSIBLE_CONFIG_DIRS)
    else:
        return path

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

def stored_pid(lockfile):
    try:
        lockfile = open(lockfile, 'r')
        pid = lockfile.read()
    finally:
        lockfile.close()
    return int(pid)

def cli_main():
    from .info import __logo__, __version__
    # Parse args
    import argparse
    parser = argparse.ArgumentParser(
        description='Yet another keyboard remapping tool for X environment.')
    parser.add_argument('-c', '--config', dest="config", metavar='config.py', type=str, nargs='?',
                        help='configuration file (See README.md for syntax)')
    parser.add_argument('-d', '--devices', dest="devices", metavar='device', type=str, nargs='+',
                        help='keyboard devices to remap (if omitted, xkeysnail choose proper keyboard devices)')
    parser.add_argument('-w', '--watch', dest='watch', action='store_true',
                        help='watch keyboard devices plug in ')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='suppress output of key events')
    parser.add_argument('-b', '--boot', dest='boot', metavar='boot', type=int,
                        help='startup delay to wait config file with systemd')
    parser.add_argument('-k', '--kill', dest='kill', action='store_true',
                        help='kill other xkeysnail instancies')
    args = parser.parse_args()

    config_diretory = config_dir_search(args.config)
    config_file = join(config_diretory, 'config.py')
    lockfile = join(config_diretory, 'lockfile')

    if not args.kill:
        print("Config file: %s" % config_file)
        if has_another_instace(lockfile):
            print('Another instance of keysnail is running, exiting.')
            exit(1)
        else:
            startup_lock(lockfile, current_pid())
        if not args.devices and not args.watch:
            print("Use --watch or --devices, more info with: xkeysnail --help.")
            sys.exit(1)

    pid = stored_pid(lockfile)
    if args.kill:
        try:
            os.kill(pid, signal.SIGUSR1)
            print("Xkeysnail, PID: %s, terminated by user." % pid)
            exit(1)
        except Exception as e:
            raise e

    # closure receiveSignal was the best option I found without
    # having to rewrite cli_main() in a class.
    def receiveSignal(signalNumber, frame):
        os.remove(lockfile)
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception as e:
            print("Xkeysnail: AccessDenied, try again with --> 'sudo xkeysnail -k'.")
            print(e)
    # Other
    signal.signal(signal.SIGUSR1, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)

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
