# -*- coding: utf-8 -*-

"""Package with methods to control Xkeysnail startup."""

import os
import sys
import psutil
import signal
from os import getpid

from os.path import join
from os.path import exists

from xkeysnail import KILL
from xkeysnail import QUIET
from xkeysnail import WATCH
from xkeysnail import DEVICE
from xkeysnail import CONFIG

from xkeysnail.input import loop
from xkeysnail.log import log_msg
from xkeysnail.log import wrap_logger
from .info import __logo__
from .info import __name__
from .info import __version__


@wrap_logger
class XkeySnail(object):
    """Class to control startup fo Xkeysnail."""

    def __init__(self) -> None:
        """__init__ xkeysnail class."""
        super().__init__()
        signal.signal(signal.SIGTERM, self.receiveSignal)
        signal.signal(signal.SIGINT, self.receiveSignal)
        self.pid = self.current_pid()
        if KILL:
            self.kill_xkeysnail(self.get_pid_in_lockfile(), signal.SIGTERM)

        if exists(CONFIG):
            self.configfile = join(CONFIG, 'config.py')
            if not exists(self.configfile):
                log_msg('Not founded config.py in path: %s' % self.configfile)
                sys.exit(0)
            self.lockfile = join(CONFIG, 'lockfile')

        if not DEVICE and not WATCH:
            log_msg('Use --watch or --devices, more info with: xkeysnail --help.')
            sys.exit(0)

        self.check_another_instance()
        self.create_lockfile_on_startup()
        self.eval_config()
        self.log_msg_logo_on_startup()
        self.check_if_uinput_device_exists()
        self.check_if_access_to_uinput()
        self.start_xkeysnail_loop()

    def receiveSignal(self, signalNumber, _):
        """Signal handler to detect linux signals."""
        self.kill_xkeysnail(self.pid, signalNumber)

    def start_xkeysnail_loop(self):
        """Start xkeysnail loop."""
        loop(DEVICE, WATCH, QUIET)

    def eval_config(self):
        """Method to eval config.py file and compile settings."""
        try:
            with open(self.configfile, "rb") as file:
                exec(compile(file.read(), self.configfile, 'exec'), globals())
        except (FileNotFoundError, TypeError):
            pass

    def check_another_instance(self):
        """Method to check other xkeysnail instance."""
        if self.lockfile_exist():
            log_msg('Another instance of keysnail is running, exiting.')
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

    @ staticmethod
    def current_pid():
        """Staticmethod to return current pid."""
        return getpid()

    @ staticmethod
    def log_msg_logo_on_startup():
        """Staticmethod to log_msg startup msg."""
        log_msg("")
        log_msg(__logo__.strip())
        log_msg("                             v{}".format(__version__))
        log_msg("")

    @ staticmethod
    def check_if_uinput_device_exists():
        """Staticmethod to check for /dev/uinput existence."""
        if not exists('/dev/uinput'):
            log_msg('The "/dev/uinput" device does not exist.')
            log_msg('Please check your kernel configuration.')
            sys.exit(1)
        return True

    @ staticmethod
    def check_if_access_to_uinput():
        """Staticmethod to check if _uinput is accessible."""
        from evdev.uinput import UInputError
        try:
            from xkeysnail.output import _uinput  # noqa: F401
            return True
        except UInputError:
            log_msg('Failed to open `uinput` in write mode.')
            if os.getuid() != 0:
                log_msg('Make sure that you have executed xkeysnail with root privileges.')
                log_msg('Such as: sudo xkeysnail -c config.py')
            sys.exit(1)

    def kill_xkeysnail(self, pid=None, sigtype=None):
        """Method with actions to be performed during finalization."""
        try:
            try:
                os.kill(pid, sigtype)
                log_msg('Process PID %s, finalized by user.' % self.pid)
            except PermissionError:
                log_msg('Xkeysnail: AccessDenied, try again with --> "sudo xkeysnail -k"')
                sys.exit(1)
            except ProcessLookupError:
                log_msg('PID process not found, xkeysnail is probably not running!')
        except RecursionError:
            pass
        finally:
            if self.lockfile_exist():
                os.remove(self.lockfile)
        sys.exit(0)
