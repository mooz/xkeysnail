# -*- coding: utf-8 -*-

"""
    Input module.
"""

import sys
from select import select
from evdev import ecodes, InputDevice, list_devices
from inotify_simple import flags, INotify

from .key import Key

from evdev.uinput import UInputError

try:
    from .output import send_event
except UInputError:
    pass

from .transform import on_event
from .transform import device_in_config


def get_devices_list():
    """Get list of InputDevices."""
    return list(map(InputDevice, reversed(list_devices())))


def is_keyboard_device(device):
    """Guess the device is a keyboard or not"""
    capabilities = device.capabilities(verbose=False)
    _keys = [
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

    if not any(k in supported_keys for k in _keys):
        # Not support common keys. Not keyboard.
        return False
    if Key.BTN_MOUSE in supported_keys:
        # Mouse.
        return False
    # Otherwise, its keyboard!
    return True


def print_device_list(devices):
    """Print a list of devices."""
    device_format = '{1.fn:<20} {1.phys:<35} {1.name}'
    try:
        device_lines = [
            device_format.format(n, d) for n, d in enumerate(devices)
        ]

        print('-' * len(max(device_lines, key=len)))
        print('{:<20} {:<35} {}'.format('Device', 'Phys', 'Name'))
        print('-' * len(max(device_lines, key=len)))
        print('\n'.join(device_lines))
        print('')

    except ValueError:
        print('error: no input devices found (do you have rw permission on /dev/input/*?)')
        sys.exit(1)


def get_devices_from_paths(device_paths):
    """Get devices with paths."""
    return list(map(InputDevice, device_paths))


def is_device_name_in_config(device):
    """Check if device is in config file."""
    return any(k == device.name for k in device_in_config)


class DeviceFilter(object):
    """Filter InputDevices."""
    def __init__(self, matches, device_watch):
        self.matches = matches
        self.watch = device_watch

    def __call__(self, device):
        # Match by device path or name, if no keyboard devices specified,
        # picks up keyboard-ish devices.
        if self.watch:
            if is_device_name_in_config(device):
                return True
        elif self.matches:
            try:
                check_device = InputDevice(self.matches[0])
                if check_device.name == "py-evdev-uinput":
                    # Exclude evdev device, we use for output emulation,
                    # from input monitoring list
                    print("The device:")
                    print(f" PATH: {check_device.fn}")
                    print(f" NAME: {check_device.name}")
                    print(" Cannot be used as it is the Xkeysnail output device,")
                    print(" provide the correct device!!")
                    sys.exit(1)
            except FileNotFoundError:
                print("Device not found!")
                print(f" PATH {self.matches[0]}, not found!")
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
            print('\nDevices declared in "config.py":')
            print("\n".join(list(map(lambda x: f"  DEVICE: {x}", device_in_config))))

    devices = list(filter(DeviceFilter(device_matches, device_watch), devices))
    if interactive:
        if not devices and device_watch:
            pass  # will continue to watch for device add/remove
        elif devices:
            print('\nOkay, remapping following device(s):\n')
        elif not devices and device_watch:
            print('Error: no input devices found')
            print(' Do you have rw permission on /dev/input/*?')
            sys.exit(1)

        if devices:
            print_device_list(devices=devices)
    return devices


def in_device_list(fn_info, devices):
    """Check if device is in list."""
    for device in devices:
        if device.fn == fn_info:
            return True
    return False


def loop(device_matches, device_watch, quiet):
    """The main loop."""
    devices = select_device(device_matches, device_watch, True)
    try:
        for device in devices:
            device.grab()
    except IOError:
        print("IOError when grabbing device.")
        print(" Maybe, another xkeysnail instance is running?")
        sys.exit(1)

    if device_watch:
        inotify = INotify()
        inotify.add_watch("/dev/input", flags.CREATE | flags.ATTRIB)
        print('\nWaiting for new devices with --watch/-w.')
    device_filter = DeviceFilter(device_matches, device_watch)
    if quiet:
        print("\nQUIET mode enabled with --quiet/-q")

    try:
        while True:
            try:
                waitables = devices[:]
                if device_watch:
                    waitables.append(inotify.fd)
                r_waitable, _, _ = select(waitables, [], [])
                for waitable in r_waitable:
                    if isinstance(waitable, InputDevice):
                        for event in waitable.read():
                            if event.type == ecodes.EV_KEY:  # pylint: disable=no-member, c-extension-no-member
                                on_event(event, waitable.name, quiet)
                            else:
                                send_event(event)
                    else:
                        new_devices = add_new_device(
                            devices, device_filter, inotify)
                        if new_devices:
                            print(f"\nDevice Added: {devices[0].name}\n")
            except OSError:
                if isinstance(waitable, InputDevice):
                    remove_device(devices, waitable)
                    if not device_watch:
                        if not devices:
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
    """Add new devices."""
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
    """Remove devices."""
    devices.remove(device)
    print("\nDevice removed: %s" % device.name)
    try:
        device.ungrab()
    except OSError:
        pass
