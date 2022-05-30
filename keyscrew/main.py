# -*- coding: utf-8 -*-

"""Package with methods to control keyscrew startup."""

import os
import sys
import signal

from os import getpid
from os.path import join, exists

import psutil
from evdev.uinput import UInputError

from keyscrew import (
    KILL,
    QUIET,
    WATCH,
    DEVICE,
    CONFIG
)

from keyscrew.input import loop
from keyscrew.log import log_msg
try:
    from keyscrew.output import _uinput as _UINPUT
except UInputError:
    _UINPUT = False

from . import __logo__
from . import __version__

class KeyScrew():
    """Class to control startup fo keyscrew."""

    def __init__(self) -> None:
        """Inits keyscrew class."""
        super().__init__()
        signal.signal(signal.SIGTERM, self.receive_signal)
        signal.signal(signal.SIGINT, self.receive_signal)
        self.pid = self.current_pid()
        self.lockfile_path = join(CONFIG, "lockfile")

        if KILL:
            self.kill_keyscrew(self.lockfile_pid(), signal.SIGTERM)

        if exists(CONFIG):
            self.configfile = join(CONFIG, "config.py")
            if not exists(self.configfile):
                log_msg(f"Not founded config.py in path: {self.configfile}")
                sys.exit(0)

        if not DEVICE and not WATCH:
            log_msg("Use --watch or --devices, more info with: keyscrew --help.")
            sys.exit(0)

        self.check_another_instance()
        self.create_lockfile_on_startup()
        self.eval_config()
        self.print_logo_on_startup()
        self.check_if_uinput_device_exists()
        self.check_if_access_to_uinput()
        self.start_keyscrew_loop()

    def receive_signal(self, signaln_umber, _):
        """Signal handler to detect linux signals."""
        self.kill_keyscrew(self.pid, signaln_umber)

    def start_keyscrew_loop(self):
        """Start keyscrew loop."""
        loop(DEVICE, WATCH, QUIET)

    def eval_config(self):
        """Method to eval config.py file and compile settings."""
        try:
            with open(self.configfile, "rb") as file:
                exec(compile(file.read(), self.configfile, 'exec'), globals())
        except (FileNotFoundError, TypeError):
            pass

    def lockfile(self):
        """Method to check if lockfile exist."""
        if exists(self.lockfile_path):
            return True

    def check_another_instance(self):
        """Method to check other keyscrew instance."""
        if self.lockfile():
            if self.check_pid_in_procs_list():
                # revise this double message
                log_msg("Another instance of keysnail is running, exiting.")
                print("Another instance of keysnail is running, exiting.")
                sys.exit(0)
        log_msg("No other instance detected.")
        log_msg(f"keyscrew start with PID: {self.pid}")

    def check_pid_in_procs_list(self):
        """Check existence of current pid in process list."""
        if self.lockfile():
            if self.lockfile_pid() in psutil.pids():
                return True
        return False

    def lockfile_pid(self):
        """Method to get pid stored in lockfile."""
        try:
            with open(self.lockfile_path, "r", encoding="utf8") as lockfile:
                try:
                    return int(lockfile.read().strip())
                finally:
                    lockfile.close()
        except (FileNotFoundError, TypeError) as getlockpiderror:
            log_msg(f"INFO -> lockfile_pid: {getlockpiderror}")

    def create_lockfile_on_startup(self):
        """Method to create lockfile on startup."""
        try:
            with open(self.lockfile_path, "w+", encoding="utf8") as lockfile:
                try:
                    lockfile.write(self.pid)
                    log_msg(f"Lockfile created with PID: {self.pid}")
                finally:
                    lockfile.close()
        except (FileNotFoundError, TypeError) as createlockfileerror:
            log_msg(f"INFO -> create_lockfile_on_startup: {createlockfileerror}")

    @staticmethod
    def current_pid():
        """Staticmethod to return current pid."""
        return str(getpid())

    @staticmethod
    def print_logo_on_startup():
        """Staticmethod to print startup msg."""
        print()
        print(__logo__.strip())
        print(f"v{__version__}")
        print()

    @ staticmethod
    def check_if_uinput_device_exists():
        """Staticmethod to check for /dev/uinput existence."""
        if not exists("/dev/uinput"):
            log_msg("The '/dev/uinput' device does not exist.")
            log_msg("Please check your kernel configuration.")
            sys.exit(1)
        return True

    @ staticmethod
    def check_if_access_to_uinput():
        """Staticmethod to check if _uinput is accessible."""
        if _UINPUT:
            return True
        else:
            log_msg("Failed to open `uinput` in write mode.")
            if os.getuid() != 0:
                log_msg("Make sure that you have executed keyscrew with root privileges.")
                log_msg("Such as: sudo keyscrew -c config.py")
            sys.exit(1)

    def kill_keyscrew(self, pid=None, sigtype=None):
        """Method with actions to be performed during finalization."""
        try:
            os.kill(pid, sigtype)
            log_msg(f"Process PID {pid}, finalized by user.")
        except (ProcessLookupError, TypeError):
            log_msg("PID process not found, keyscrew is probably not running!")
        except PermissionError:
            log_msg("keyscrew: AccessDenied, try again with --> 'sudo keyscrew -k'")
            sys.exit(1)
        except RecursionError:
            pass
        finally:
            if self.lockfile():
                os.remove(self.lockfile_path)
        sys.exit(0)
