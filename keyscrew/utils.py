
import re
from shutil import which
from subprocess import Popen

from keyscrew.transform import Key
from keyscrew.transform import Combo
from keyscrew.transform import create_modifiers_from_strings

# ============================================================ #
# Utility functions for keymap
# ============================================================ #


def launch(command, multplier=None):
    """Method to launch command in config."""

    if multplier:
        command = ([command] * multplier)

    def notinpath(args):
        """Check existence of command in $PATH"""
        if not any(which(k) for k in args):
            print()
            print("Commands not found in $PATH, enter the absolute path.")
            print()
            return
        # TODO: Currently, the commands are run as root, in a
        # way that's a problem, looking for a solution to that.
        Popen(args, start_new_session=True)

    def launcher():
        """Launch command."""
        if multplier:
            for cmd_block in command:
                args = cmd_block if len(
                    cmd_block) > 1 else cmd_block[0].split(' ')
                notinpath(args)
        else:
            args = command if len(command) > 1 else command[0].split(' ')
            notinpath(args)

    if multplier:
        return launcher, 'launch(%s, x%s)' % (command[0], multplier)
    else:
        return launcher, 'launch(%s)' % command


def sleep(sec):
    """Sleep sec in commands."""
    def sleeper():
        import time
        time.sleep(sec)
    return sleeper, 'sleep(%s)' % sec

# ============================================================ #


def K(exp):
    """Helper function to specify keymap."""
    modifier_strs = []
    while True:
        m = re.match(
            r"\A(LC|LCtrl|RC|RCtrl|C|Ctrl|LM|LAlt|RM|RAlt|M|Alt|LShift|RShift|Shift|LSuper|LWin|RSuper|RWin|Super|Win)-", exp)
        if m is None:
            break
        modifier = m.group(1)
        modifier_strs.append(modifier)
        exp = re.sub(r"\A{}-".format(modifier), "", exp)
    key_str = exp.upper()
    key = getattr(Key, key_str)
    return Combo(create_modifiers_from_strings(modifier_strs), key)
