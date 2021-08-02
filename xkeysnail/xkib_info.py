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
        # except Exception:
        except Xlib.error.DisplayConnectionError as Display_error:
            if not log_count:
                log_count = True
                log_msg(Display_error)
            os.system("xhost +SI:localuser:root")
            time = - 1
    return None


def get_active_window_wm_class():
    """Get active window's WM_CLASS."""
    display = get_display()
    if not display:
        sys.exit(0)
    pair = get_class_name(display.get_input_focus().focus)
    if pair:
        # (process name, class name)
        return str(pair[1])
    return ""


def get_class_name(window):
    """Get window's class name (recursively checks parents)."""
    wmname = window.get_wm_name()
    wmclass = window.get_wm_class()
    # workaround for Java app
    # https://github.com/JetBrains/jdk8u_jdk/blob/master/src/solaris/classes/sun/awt/X11/XFocusProxyWindow.java#L35
    if not wmclass and not wmname or "FocusProxy" in wmclass:
        parent_window = window.query_tree().parent
        if parent_window:
            return get_class_name(parent_window)
    elif wmclass and not wmname:
        return wmclass
    return None
