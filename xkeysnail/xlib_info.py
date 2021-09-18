# -*- coding: utf-8 -*-

"""Modules with methods related to xlib."""

import Xlib
from Xlib.display import Display

from xkeysnail.log import log_msg


def get_window_info(window):
    """Get window's info (recursively checks parents)."""
    try:
        try:
            wmname = window.get_wm_name().lower()
            # (process name, class name)
            wmclass = window.get_wm_class()[1].lower()
        except TypeError:
            wmclass = window.get_wm_class().lower()
            pass
        # workaround for Java app
        # https://github.com/JetBrains/jdk8u_jdk/blob/master/src/solaris/classes/sun/awt/X11/XFocusProxyWindow.java#L35
        if not wmclass and not wmname or "FocusProxy" in wmclass:
            parent_window = window.query_tree().parent
            if parent_window:
                return get_window_info(parent_window)
        return {'wmclass': str(wmclass), 'wmname': wmname}
    except AttributeError:
        pass
    return {'wmclass': '', 'wmname': ''}


def get_display(display=None, time=30):
    """Function to wait and get Display."""
    while not time == 0:
        try:
            return Display()
        except Xlib.error.DisplayConnectionError:
            time =- 1
        except Xlib.error.ConnectionClosedError as Xlib_ConnectionClosedError:
            log_msg('Xlib: %s ' % Xlib_ConnectionClosedError)
            return Display()
    return None


def get_focused_window(display):
    return display.get_input_focus().focus


def get_wmclass(display=get_display()):
    """Return active window's WM_CLASS."""
    in_focus_window = get_focused_window(display)
    return get_window_info(in_focus_window)['wmclass']


def get_wmname(display=get_display()):
    """Return active window's WM_NAME."""
    in_focus_window = get_focused_window(display)
    return get_window_info(in_focus_window)['wmname']
