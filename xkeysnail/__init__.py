# -*- coding: utf-8 -*-

"""Package with methos to control Xkeysnail startup."""

import os
import sys
from xkeysnail.log import print, wrap_logger
import psutil
import signal
from os import getpid

from time import sleep
from os.path import join
from os.path import exists

from xkeysnail.input import loop
from .info import __logo__, __version__


@wrap_logger
class XkeySnail(object):
    """Class to control startup fo Xkeysnail."""

    def __init__(self, configpath, args) -> None:
        """__init__ xkeysnail class."""
        super().__init__()
        signal.signal(signal.SIGTERM, self.receiveSignal)
        signal.signal(signal.SIGINT, self.receiveSignal)
        configpath = self.search_for_configdir(configpath)
        self.args = args
        self.pid = self.current_pid()

        if exists(configpath):
            self.configfile = self.wait_config(
                join(configpath, 'config.py'), args.boot)
            self.lockfile = join(configpath, 'lockfile')
        if args.kill:
            self.kill_xkeysnail(self.get_pid_in_lockfile(), signal.SIGTERM)

        if not self.args.devices and not self.args.watch:
            print('Use --watch or --devices, more info with: xkeysnail --help.')
            sys.exit(0)

        self.check_another_instance()
        self.create_lockfile_on_startup()
        self.eval_config()
        self.print_logo_on_startup()
        self.check_if_uinput_device_exists()
        self.check_if_access_to_uinput()
        self.start_xkeysnail_loop()

    def receiveSignal(self, signalNumber, _):
        """Signal handler to detect linux signals."""
        self.kill_xkeysnail(self.pid, signalNumber)

    def start_xkeysnail_loop(self):
        """Start xkeysnail loop."""
        loop(self.args.devices, self.args.watch, self.args.quiet)

    def eval_config(self):
        """Method to eval config.py file and compile settings."""
        try:
            with open(self.configfile, "rb") as file:
                exec(compile(file.read(), self.configfile, 'exec'), globals())
        except (FileNotFoundError, TypeError):
            pass

    def wait_config(self, file_path, wait_time):
        """Method to wait for config.py file on startup."""
        founded_messege = "Config file founded: %s" % file_path
        if not os.path.isfile(file_path):
            if wait_time:
                print('Startup delay enable, wait for %s' % wait_time)
            for _ in range(wait_time if wait_time else 0):
                sleep(1)
                if os.path.isfile(file_path):
                    print(founded_messege)
                    return file_path
            print('Config.py not found, use --config or place config.py in %s'
                  % file_path)
            sys.exit(0)
        else:
            print(founded_messege)
            return file_path

    def check_another_instance(self):
        """Method to check other xkeysnail instance."""
        if self.lockfile_exist():
            print('Another instance of keysnail is running, exiting.')
            sys.exit(0)

    def lockfile_exist(self):
        """Method to check if lockfile exist."""
        return os.path.exists(self.lockfile)

    def check_pid_in_procs_list(self):
        """Check existence of current pid in process list."""
        if os.path.exists(self.lockfile):
            if self.get_pid_in_lockfile() in psutil.pids():
                return True
        return False

    def get_pid_in_lockfile(self):
        """Method to get pid stored in lockfile."""
        try:
            with open(self.lockfile, 'r') as lockfile:
                try:
                    self.pid = int(lockfile.read())
                finally:
                    lockfile.close()
                return self.pid
        except FileNotFoundError:
            pass
        return False

    def create_lockfile_on_startup(self):
        """Method to create lockfile on startup."""
        try:
            with open(self.lockfile, 'w+') as lockfile:
                try:
                    lockfile.write(str(self.pid))
                finally:
                    lockfile.close()
        except FileExistsError:
            pass

    @staticmethod
    def current_pid():
        """Staticmethod to return current pid."""
        return getpid()

    @staticmethod
    def search_for_configdir(path):
        """Staticmethod to search config diretory."""
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

    @staticmethod
    def print_logo_on_startup():
        """Staticmethod to print startup msg."""
        print("")
        print(__logo__.strip())
        print("                             v{}".format(__version__))
        print("")

    @staticmethod
    def check_if_uinput_device_exists():
        """Staticmethod to check for /dev/uinput existence."""
        if not exists('/dev/uinput'):
            print('The "/dev/uinput" device does not exist.')
            print('Please check your kernel configuration.')
            sys.exit(1)
        return True

    @staticmethod
    def check_if_access_to_uinput():
        """Staticmethod to check if _uinput is accessible."""
        from evdev.uinput import UInputError
        try:
            from xkeysnail.output import _uinput  # noqa: F401
            return True
        except UInputError:
            print('Failed to open `uinput` in write mode.')
            if os.getuid() != 0:
                print('Make sure that you have executed xkeysnail with root privileges.')
                print('Such as: sudo xkeysnail -c config.py')
            sys.exit(1)

    def kill_xkeysnail(self, pid=None, sigtype=None):
        """Method with actions to be performed during finalization."""
        try:
            try:
                os.kill(pid, sigtype)
                print('Process PID %s, finalized by user.' % self.pid)
            except PermissionError:
                print('Xkeysnail: AccessDenied, try again with --> "sudo xkeysnail -k"')
                sys.exit(1)
            except ProcessLookupError:
                print('PID process not found, xkeysnail is probably not running!')
        except RecursionError:
            pass
        finally:
            if self.lockfile_exist():
                os.remove(self.lockfile)
        sys.exit(0)
