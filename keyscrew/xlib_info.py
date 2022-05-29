# -*- coding: utf-8 -*-

"""Modules with methods related to xlib."""

from Xlib.display import Display
from Xlib.error import ConnectionClosedError, DisplayConnectionError

from keyscrew.log import log_msg


def get_window_info(window):
    """This method return the current window in WM_NAME, WM_CLASS."""
    try:
        try:
            wmname = window.get_wm_name().lower()
            # (process name, class name)
            wmclass = window.get_wm_class()[1].lower()
        except TypeError:
            wmclass = window.get_wm_class().lower()
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


def get_display(time=30):
    """This method wait for Display() and return if is available."""
    while time != 0:
        try:
            return Display()
        except DisplayConnectionError:
            time =- 1
        except ConnectionClosedError as connectionclosederror:
            log_msg(f"Xlib: {connectionclosederror}")
            return Display()
    return None


def get_focused_window(display):
    """This method return the current focused window."""
    return display.get_input_focus().focus


def get_wmclass(display=get_display()):
    """This method return the current window WM_CLASS."""
    in_focus_window = get_focused_window(display)
    return get_window_info(in_focus_window)['wmclass']


def get_wmname(display=get_display()):
    """This method return the current window WM_NAME."""
    in_focus_window = get_focused_window(display)
    return get_window_info(in_focus_window)['wmname']
