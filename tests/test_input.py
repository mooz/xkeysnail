# -*- coding: utf-8 -*-
"""Device listing and matching tests for InputDevice.path.

python-evdev 1.9 removed InputDevice.fn. These tests stub InputDevice so
they do not need /dev/input, and they fail if device-node lookups use .fn.
"""

import io
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

# Prefer the checkout when running from a git working tree. Set
# XKEYSNAIL_TEST_INSTALLED=1 to import the copy installed on the system
# (for example the files from the arm64 .deb).
if os.environ.get("XKEYSNAIL_TEST_INSTALLED") != "1":
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)


def _install_import_stubs():
    """Let xkeysnail.input import without evdev, Xlib, or /dev/uinput."""
    evdev = types.ModuleType("evdev")
    evdev.ecodes = types.SimpleNamespace()
    evdev.InputDevice = None
    evdev.list_devices = lambda: []
    sys.modules["evdev"] = evdev

    import xkeysnail

    transform = types.ModuleType("xkeysnail.transform")
    transform.on_event = lambda *args, **kwargs: None
    output = types.ModuleType("xkeysnail.output")
    output.send_event = lambda *args, **kwargs: None
    sys.modules["xkeysnail.transform"] = transform
    sys.modules["xkeysnail.output"] = output
    xkeysnail.transform = transform
    xkeysnail.output = output


_install_import_stubs()

import xkeysnail.input as input_module  # noqa: E402
from xkeysnail.input import (  # noqa: E402
    DeviceFilter,
    add_new_device,
    get_devices_from_paths,
    get_devices_list,
    in_device_list,
    is_keyboard_device,
    print_device_list,
    select_device,
)
from xkeysnail.key import Key  # noqa: E402


def _keyboard_caps(extra=()):
    keys = [Key.SPACE, Key.A, Key.Z]
    keys.extend(extra)
    return {1: list(keys)}


class FakeDevice(object):
    """Stand-in for evdev.InputDevice after InputDevice.fn was removed."""

    def __init__(self, path, name="Test Keyboard", phys="usb-phys",
                 capabilities=None, grab_error=False):
        self.path = path
        self.fd = 17
        self.name = name
        self.phys = phys
        self._capabilities = {} if capabilities is None else capabilities
        self.grab_error = grab_error
        self.grabbed = False

    @property
    def fn(self):
        raise AssertionError(
            "InputDevice.fn was removed in python-evdev >= 1.9; use .path")

    def capabilities(self, verbose=False):
        return self._capabilities

    def grab(self):
        if self.grab_error:
            raise IOError("device busy")
        self.grabbed = True


class PrintDeviceListTests(unittest.TestCase):
    def test_formats_path_name_and_phys_without_fn(self):
        device = FakeDevice(
            "/dev/input/event3",
            name="AT Translated Set 2 keyboard",
            phys="isa0060/serio0/input0",
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            print_device_list([device])
        text = buf.getvalue()
        self.assertIn("Device", text)
        data_lines = [
            line for line in text.splitlines()
            if line.startswith("/dev/input/event3")
        ]
        self.assertEqual(len(data_lines), 1)
        line = data_lines[0]
        self.assertLess(line.index("/dev/input/event3"),
                        line.index("AT Translated Set 2 keyboard"))
        self.assertLess(line.index("AT Translated Set 2 keyboard"),
                        line.index("isa0060/serio0/input0"))
        # .fd is the open file descriptor, not the device node.
        self.assertFalse(line.startswith("17"))

    def test_lists_every_device_path(self):
        devices = [
            FakeDevice("/dev/input/event1", name="One", phys="p1"),
            FakeDevice("/dev/input/event2", name="Two", phys="p2"),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            print_device_list(devices)
        text = buf.getvalue()
        self.assertIn("/dev/input/event1", text)
        self.assertIn("/dev/input/event2", text)


class DeviceFilterTests(unittest.TestCase):
    def test_matches_device_path(self):
        filt = DeviceFilter(["/dev/input/event2"])
        self.assertTrue(filt(FakeDevice("/dev/input/event2", name="Other")))
        self.assertFalse(filt(FakeDevice("/dev/input/event9", name="Other")))

    def test_matches_device_name(self):
        filt = DeviceFilter(["HHKB Professional"])
        device = FakeDevice("/dev/input/event1", name="HHKB Professional")
        self.assertTrue(filt(device))

    def test_does_not_treat_fd_as_device_node(self):
        device = FakeDevice("/dev/input/event1", name="Keyboard")
        self.assertFalse(DeviceFilter(["17"])(device))
        self.assertFalse(DeviceFilter([17])(device))

    def test_rejects_when_neither_path_nor_name_matches(self):
        filt = DeviceFilter(["/dev/input/event0", "Some Other Keyboard"])
        device = FakeDevice("/dev/input/event4", name="Built-in Keyboard")
        self.assertFalse(filt(device))

    def test_without_matches_keeps_keyboard_and_drops_mouse(self):
        filt = DeviceFilter(None)
        keyboard = FakeDevice("/dev/input/event0", capabilities=_keyboard_caps())
        mouse = FakeDevice(
            "/dev/input/event1",
            name="Mouse",
            capabilities=_keyboard_caps([Key.BTN_MOUSE]),
        )
        self.assertTrue(is_keyboard_device(keyboard))
        self.assertFalse(is_keyboard_device(mouse))
        self.assertTrue(filt(keyboard))
        self.assertFalse(filt(mouse))

    def test_without_matches_drops_non_keyboards_and_uinput(self):
        filt = DeviceFilter([])
        no_keys = FakeDevice("/dev/input/event5", capabilities={1: [Key.A]})
        no_ev_key = FakeDevice("/dev/input/event6", capabilities={})
        uinput = FakeDevice(
            "/dev/input/event7",
            name="py-evdev-uinput",
            capabilities=_keyboard_caps(),
        )
        self.assertFalse(filt(no_keys))
        self.assertFalse(filt(no_ev_key))
        self.assertFalse(filt(uinput))


class InDeviceListTests(unittest.TestCase):
    def test_matches_by_path_not_fd(self):
        devices = [FakeDevice("/dev/input/event4", name="Kbd")]
        self.assertTrue(in_device_list("/dev/input/event4", devices))
        self.assertFalse(in_device_list("/dev/input/event5", devices))
        self.assertFalse(in_device_list(17, devices))
        self.assertFalse(in_device_list("17", devices))


class DeviceDiscoveryTests(unittest.TestCase):
    def test_get_devices_list_wraps_paths_in_reverse(self):
        paths = ["/dev/input/event0", "/dev/input/event2"]

        def factory(path):
            return FakeDevice(path)

        with patch.object(input_module, "list_devices", return_value=list(paths)), \
                patch.object(input_module, "InputDevice", side_effect=factory):
            devices = get_devices_list()
        self.assertEqual(
            [device.path for device in devices],
            ["/dev/input/event2", "/dev/input/event0"],
        )

    def test_get_devices_from_paths_preserves_order(self):
        paths = ["/dev/input/event8", "/dev/input/event1"]

        def factory(path):
            return FakeDevice(path, name="n-" + path)

        with patch.object(input_module, "InputDevice", side_effect=factory):
            devices = get_devices_from_paths(paths)
        self.assertEqual([device.path for device in devices], paths)
        self.assertEqual(devices[0].name, "n-/dev/input/event8")

    def test_select_device_filters_by_path(self):
        library = [
            FakeDevice("/dev/input/event0", name="Built-in",
                       capabilities=_keyboard_caps()),
            FakeDevice("/dev/input/event3", name="External",
                       capabilities=_keyboard_caps()),
        ]
        by_path = {device.path: device for device in library}

        with patch.object(input_module, "list_devices",
                          return_value=list(by_path)), \
                patch.object(input_module, "InputDevice",
                             side_effect=lambda path: by_path[path]):
            selected = select_device(["/dev/input/event3"], interactive=False)
        self.assertEqual([device.path for device in selected],
                         ["/dev/input/event3"])

    def test_select_device_interactive_prints_paths(self):
        library = [
            FakeDevice("/dev/input/event0", name="Built-in",
                       phys="isa", capabilities=_keyboard_caps()),
            FakeDevice("/dev/input/event3", name="External",
                       phys="usb", capabilities=_keyboard_caps()),
        ]
        by_path = {device.path: device for device in library}
        buf = io.StringIO()
        with patch.object(input_module, "list_devices",
                          return_value=list(by_path)), \
                patch.object(input_module, "InputDevice",
                             side_effect=lambda path: by_path[path]), \
                redirect_stdout(buf):
            selected = select_device(["External"], interactive=True)
        text = buf.getvalue()
        self.assertEqual([device.path for device in selected],
                         ["/dev/input/event3"])
        self.assertIn("/dev/input/event0", text)
        self.assertIn("/dev/input/event3", text)
        self.assertIn("enable remapping", text)

    def test_select_device_interactive_exits_when_nothing_matches(self):
        library = [
            FakeDevice("/dev/input/event0", name="Built-in",
                       capabilities=_keyboard_caps()),
        ]
        by_path = {device.path: device for device in library}
        with patch.object(input_module, "list_devices",
                          return_value=list(by_path)), \
                patch.object(input_module, "InputDevice",
                             side_effect=lambda path: by_path[path]):
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    select_device(["/dev/input/missing"], interactive=True)
        self.assertEqual(raised.exception.code, 1)


class AddNewDeviceTests(unittest.TestCase):
    def _inotify(self, names):
        events = [types.SimpleNamespace(name=name) for name in names]
        return types.SimpleNamespace(read=lambda: events)

    def test_adds_device_by_path_and_grabs_it(self):
        created = []

        def factory(path):
            device = FakeDevice(path, capabilities=_keyboard_caps())
            created.append(device)
            return device

        with patch.object(input_module, "InputDevice", side_effect=factory):
            devices = []
            added = add_new_device(
                devices, DeviceFilter(None), self._inotify(["event7"]))
        self.assertEqual(created[0].path, "/dev/input/event7")
        self.assertTrue(created[0].grabbed)
        self.assertEqual(added, created)
        self.assertEqual(devices, created)

    def test_skips_duplicate_path(self):
        existing = FakeDevice("/dev/input/event1", capabilities=_keyboard_caps())

        def factory(path):
            return FakeDevice(path, name="replug", capabilities=_keyboard_caps())

        with patch.object(input_module, "InputDevice", side_effect=factory):
            devices = [existing]
            added = add_new_device(
                devices, DeviceFilter(None), self._inotify(["event1"]))
        self.assertEqual(added, [])
        self.assertEqual(devices, [existing])

    def test_skips_when_filter_rejects(self):
        def factory(path):
            return FakeDevice(path, name="not-the-one")

        with patch.object(input_module, "InputDevice", side_effect=factory):
            devices = []
            added = add_new_device(
                devices,
                DeviceFilter(["/dev/input/event9"]),
                self._inotify(["event4"]),
            )
        self.assertEqual(added, [])
        self.assertEqual(devices, [])

    def test_ignores_grab_ioerror(self):
        def factory(path):
            return FakeDevice(
                path, capabilities=_keyboard_caps(), grab_error=True)

        buf = io.StringIO()
        with patch.object(input_module, "InputDevice", side_effect=factory), \
                redirect_stdout(buf):
            devices = []
            added = add_new_device(
                devices, DeviceFilter(None), self._inotify(["event8"]))
        self.assertEqual(added, [])
        self.assertEqual(devices, [])
        self.assertIn("IOError", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
