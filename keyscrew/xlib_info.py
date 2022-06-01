# -*- coding: utf-8 -*-

"""Modules with methods related to xlib."""

from Xlib.display import Display
from Xlib.protocol import request

from Xlib.error import ConnectionClosedError, DisplayConnectionError

from keyscrew.log import log_msg


class CurrentWindowInfo(Display):
    """Class to get and return information abount current focused window."""

    def __init__(self, display=None):   # pylint: disable=useless-super-delegation
        """inits from CurrentWindowInfo."""
        super().__init__(display)
        # self.desktop_environment = os.environ["XDG_CURRENT_DESKTOP"]
        # print(self.desktop_environment)

    def get_window_info(self):
        """This method return the current window info WM_NAME and WM_CLASS."""
        dict_info = {
            'wmclass': '',
            'wmname': '',
            'fullscreen': False,
            'resolution': {
                'width': '',
                'height': ''
            }
        }

        window = self.get_focused_window()
        desktop_resolution = self.get_desktop_resolution()

        wm_geometry_data = window.get_geometry()._data  # pylint: disable=protected-access

        current_window_width = wm_geometry_data['width']
        current_window_height = wm_geometry_data['height']

        try:
            try:
                wmname = window.get_wm_name().lower()
                # (process name, class name)
                wmclass = window.get_wm_class()[1].lower()
            except TypeError:
                wmclass = window.get_wm_class().lower()

            # Desktop environments in general should appear in fullscreen,
            # generating false positives, a way to ignore them is necessary.
            # get this info from sistem is the better way
            if wmclass not in ["xfdesktop", "plasmashell"]:
                if (current_window_width == desktop_resolution['width']) and \
                        (current_window_height == desktop_resolution['height']):
                    dict_info['fullscreen'] = True

            # workaround for Java app
            # https://github.com/JetBrains/jdk8u_jdk/blob/master/src/solaris/classes/sun/awt/X11/XFocusProxyWindow.java#L35
            if not wmclass and not wmname or "FocusProxy" in wmclass:
                parent_window = self.query_tree().parent
                if parent_window:
                    return window

            dict_info["wmclass"] = wmclass
            dict_info["wmname"] = wmname
            dict_info["resolution"]["width"] = current_window_width
            dict_info["resolution"]["height"] = current_window_height

            return dict_info
        except AttributeError:
            pass
        return dict_info

    def get_desktop_resolution(self):
        """Get desktop resolution."""
        screen = self.screen()
        return {
            'width': screen.width_in_pixels,
            'height': screen.height_in_pixels
        }

    def get_focused_window(self) -> request.GetInputFocus:
        """This method return the current focused window."""
        return self.get_input_focus().focus

    def get_wmclass(self):
        """This method return the current window WM_CLASS."""
        return self.get_window_info()['wmclass']

    def get_wmname(self):
        """This method return the current window WM_NAME."""
        return self.get_window_info()['wmname']


def wait_for_display(time=30) -> CurrentWindowInfo:
    """Method to wait for Display() and return if is available."""
    while time != 0:
        try:
            return CurrentWindowInfo()
        except DisplayConnectionError:
            time = - 1
        except ConnectionClosedError as connectionclosederror:
            log_msg(f"Xlib: {connectionclosederror}")
    return None


if __name__ == "__main__":
    from time import sleep

    wm = CurrentWindowInfo()
    while True:
        sleep(0.100)
        print(wm.get_window_info())
