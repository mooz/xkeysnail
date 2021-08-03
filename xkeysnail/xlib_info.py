# -*- coding: utf-8 -*-

"""Modules with methods related to xlib."""

import os
import sys
import Xlib.display

from xkeysnail.log import log_msg


def get_display(display=None, time=10):
    """Function to wait and get Display."""
    log_count = False
    while not time == 0:
        try:
            display = Xlib.display.Display()
            return display
        # Xlib.error.DisplayConnectionError
        # This solution is under test, I don't know when and why the
        # error occurs, my theory is that during boot, it is not possible
        # to connect to the display because it is not available, waiting
        # for the display can be a solution.
        except Xlib.error.DisplayConnectionError as Display_error:
            if not log_count:
                log_count = True
                log_msg(Display_error)
            os.system("xhost +SI:localuser:root")
            time =- 1
    return None


def get_focused_window(display=get_display()):
    if not display:
        sys.exit(0)
    return display.get_input_focus().focus


def get_window_info(window=get_focused_window()):
    """Get all info from focused window's (recursively checks parents)."""
    try:
        wmclass = window.get_wm_class()[0]
    except TypeError:
        wmclass = window.get_wm_class()
    # workaround for Java app
    # https://github.com/JetBrains/jdk8u_jdk/blob/master/src/solaris/classes/sun/awt/X11/XFocusProxyWindow.java#L35
    if not wmclass or "FocusProxy" in wmclass:
        parent_window = window.query_tree().parent
        if parent_window:
            return get_window_info(parent_window)
    return {'wmname': window.get_wm_name(), 'wmclass': wmclass}


def get_wmclass():
    """Return window's wmclass."""
    return get_window_info()['wmclass']


def get_wmname():
    """Return window's wmname."""
    return get_window_info()['wmname']
