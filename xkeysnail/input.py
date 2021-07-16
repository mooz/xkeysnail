# -*- coding: utf-8 -*-

import sys
from select import select
from evdev import ecodes, InputDevice, list_devices

from .key import Key
from .output import send_event
from .transform import on_event, device_in_config

__author__ = 'zh'

start_flag = None


def get_devices_list():
    return [InputDevice(device_fn) for device_fn in reversed(list_devices())]


def is_keyboard_device(device):
    """Guess the device is a keyboard or not"""
    capabilities = device.capabilities(verbose=False)
    _KEYS = [
        Key.SPACE,
        Key.ENTER,
        Key.KEY_0,
        Key.KEY_5,
        Key.KEY_9,
        Key.ESC,
        Key.UP,
        Key.LEFT,
        Key.RIGHT,
        Key.DOWN
    ]

    if 1 not in capabilities:
        return False
    supported_keys = capabilities[1]

    if not any(k in supported_keys for k in _KEYS):
        # Not support common keys. Not keyboard.
        return False
    if Key.BTN_MOUSE in supported_keys:
        # Mouse.
        return False
    # Otherwise, its keyboard!
    return True


def print_device_list(devices):
    device_format = '{1.fn:<20} {1.phys:<35} {1.name}'
    try:
        device_lines = [device_format.format(
            n, d) for n, d in enumerate(devices)]
        print('-' * len(max(device_lines, key=len)))
        print('{:<20} {:<35} {}'.format('Device', 'Phys', 'Name'))
        print('-' * len(max(device_lines, key=len)))
        print('\n'.join(device_lines))
        print('')

    except ValueError:
        print('error: no input devices found (do you have rw permission on /dev/input/*?)')
        sys.exit(1)


def get_devices_from_paths(device_paths):
    return [InputDevice(device_fn) for device_fn in device_paths]


def is_device_name_in_config(device):
    return any(k == device.name for k in device_in_config)


class DeviceFilter(object):
    def __init__(self, matches, device_watch):
        self.matches = matches
        self.watch = device_watch

    def __call__(self, device):
        # Match by device path or name, if no keyboard devices specified, picks up keyboard-ish devices.
        if self.watch:
            if is_device_name_in_config(device):
                return True
        elif self.matches:
            try:
                check_device = InputDevice(self.matches[0])
                if check_device.name == "py-evdev-uinput":
                    # Exclude evdev device, we use for output emulation, from input monitoring list
                    print('The device:')
                    print(' PATH: %s' % check_device.fn)
                    print(' NAME: %s' % check_device.name)
                    print(' Cannot be used as it is the Xkeysnail output device,')
                    print(' provide the correct device!!')
                    sys.exit(1)
            except FileNotFoundError:
                print('Device not found!')
                print(' PATH %s, not found!' % self.matches[0])
                sys.exit(1)

            for match in self.matches:
                if device.fn == match or device.name == match:
                    return True
            return False
        # Exclude none keyboard devices
        if not is_keyboard_device(device):
            return False


def select_device(device_matches=None, device_watch="global", interactive=True):
    """Select a device from the list of accessible input devices."""
    devices = get_devices_from_paths(reversed(list_devices()))

    if interactive:
        print_device_list(devices=devices)
        if not device_matches:
            print('\n\nXkeysnail picks up keyboard devices in config.py!')

    devices = list(filter(DeviceFilter(device_matches, device_watch), devices))
    if interactive:
        if not devices and device_watch:
            pass  # will continue to watch for device add/remove
        elif devices:
            print(
                ' '.join(
                    [
                        'Okay, now enabling remapping',
                        'for the following pre-configured device(s):\n'
                    ]
                )
            )
        elif not devices and device_watch:
            print(
                ' '.join(
                    [
                        'error: no input devices found',
                        '(do you have rw permission on /dev/input/*?)'
                    ]
                )
            )
            sys.exit(1)

        if devices:
            print_device_list(devices=devices)
    return devices


def in_device_list(fn, devices):
    for device in devices:
        if device.fn == fn:
            return True
    return False

def loop(device_matches, device_watch, quiet):
    global start_flag
    devices = select_device(device_matches, device_watch, True)
    try:
        for device in devices:
            device.grab()
    except IOError:
        print("IOError when grabbing device. Maybe, another xkeysnail instance is running?")
        sys.exit(1)

    if device_watch:
        start_flag = True
        from inotify_simple import INotify, flags
        inotify = INotify()
        inotify.add_watch("/dev/input", flags.CREATE | flags.ATTRIB)
        print('Option --watch enable, waiting for devices')
    device_filter = DeviceFilter(device_matches, device_watch)
    if quiet:
        print("No key event will be output since quiet option was specified.")

    try:
        while True:
            try:
                waitables = devices[:]
                if device_watch:
                    waitables.append(inotify.fd)
                r, _, _ = select(waitables, [], [])
                for waitable in r:
                    if isinstance(waitable, InputDevice):
                        for event in waitable.read():
                            if event.type == ecodes.EV_KEY:  # pylint: disable=no-member
                                on_event(event, waitable.name, quiet)
                            else:
                                send_event(event)
                    else:
                        new_devices = add_new_device(
                            devices, device_filter, inotify)
                        if new_devices:
                            if start_flag is None:
                                print(
                                    "Okay, now enable remapping on the following devices founded:\n")
                            print("\nDevice Added: %s\n" % devices[0].name)
            except OSError:
                if isinstance(waitable, InputDevice):
                    remove_device(devices, waitable)
                    if not device_watch:
                        if not len(devices):
                            break
    finally:
        for device in devices:
            try:
                device.ungrab()
            except OSError:
                pass
        if device_watch:
            inotify.close()


def add_new_device(devices, device_filter, inotify):
    new_devices = []
    for event in inotify.read():
        new_device = InputDevice("/dev/input/" + event.name)
        if device_filter(new_device) and not in_device_list(new_device.fn, devices):
            try:
                new_device.grab()
            except IOError:
                # Ignore errors on new devices
                print("IOError when grabbing new device: " + str(new_device.name))
                continue
            devices.append(new_device)
            new_devices.append(new_device)
    return new_devices


def remove_device(devices, device):
    devices.remove(device)
    print("\nDevice removed: %s" % device.name)
    try:
        device.ungrab()
    except OSError:
        pass
