# -*- coding: utf-8 -*-

from evdev import ecodes, InputDevice, list_devices
from select import select
from sys import exit
from .transform import on_event
from .output import send_event
from .key import Key

__author__ = 'zh'


def get_devices_list():
    return [InputDevice(device_fn) for device_fn in reversed(list_devices())]


def is_keyboard_device(device):
    """Guess the device is a keyboard or not"""
    capabilities = device.capabilities(verbose=False)
    if 1 not in capabilities:
        return False
    supported_keys = capabilities[1]
    if Key.SPACE not in supported_keys or \
       Key.A not in supported_keys or \
       Key.Z not in supported_keys:
        # Not support common keys. Not keyboard.
        return False
    if Key.BTN_MOUSE in supported_keys:
        # Mouse.
        return False
    # Otherwise, its keyboard!
    return True


def print_device_list(devices):
    device_format = '{1.fn:<20} {1.name:<35} {1.phys}'
    device_lines = [device_format.format(n, d) for n, d in enumerate(devices)]
    print('-' * len(max(device_lines, key=len)))
    print('{:<20} {:<35} {}'.format('Device', 'Name', 'Phys'))
    print('-' * len(max(device_lines, key=len)))
    print('\n'.join(device_lines))
    print('')


def get_devices_from_paths(device_paths):
    return [InputDevice(device_fn) for device_fn in device_paths]


class DeviceFilter(object):
    def __init__(self, matches):
        self.matches = matches

    def __call__(self, device):
        # Match by device path or name, if no keyboard devices specified, picks up keyboard-ish devices.
        if self.matches:
            for match in self.matches:
                if device.fn == match or device.name == match:
                    return True
            return False
        # Exclude none keyboard devices
        if not is_keyboard_device(device):
            return False
        # Exclude evdev device, we use for output emulation, from input monitoring list
        if device.name == "py-evdev-uinput":
            return False
        return True


def select_device(device_matches=None, interactive=True):
    """Select a device from the list of accessible input devices."""
    devices = get_devices_from_paths(reversed(list_devices()))

    if interactive:
        if not device_matches:
            print("""No keyboard devices specified via (--devices) option.
xkeysnail picks up keyboard-ish devices from the list below:
""")
        print_device_list(devices)

    devices = list(filter(DeviceFilter(device_matches), devices))

    if interactive:
        if not devices:
            print('error: no input devices found (do you have rw permission on /dev/input/*?)')
            exit(1)

        print("Okay, now enable remapping on the following device(s):\n")
        print_device_list(devices)

    return devices


def in_device_list(fn, devices):
    for device in devices:
        if device.fn == fn:
            return True
    return False


def loop(device_matches, device_watch, quiet):
    devices = select_device(device_matches, True)
    try:
        for device in devices:
            device.grab()
    except IOError:
        print("IOError when grabbing device. Maybe, another xkeysnail instance is running?")
        exit(1)

    if device_watch:
        from inotify_simple import INotify, flags
        inotify = INotify()
        inotify.add_watch("/dev/input", flags.CREATE | flags.ATTRIB)
        print("Watching keyboard devices plug in")
    device_filter = DeviceFilter(device_matches)

    if quiet:
        print("No key event will be output since quiet option was specified.")

    try:
        while True:
            try:
                waitables = devices[:]
                if device_watch:
                    waitables.append(inotify.fd)
                r, w, x = select(waitables, [], [])

                for waitable in r:
                    if isinstance(waitable, InputDevice):
                        for event in waitable.read():
                            if event.type == ecodes.EV_KEY:
                                on_event(event, waitable.name, quiet)
                            else:
                                send_event(event)
                    else:
                        new_devices = add_new_device(devices, device_filter, inotify)
                        if new_devices:
                            print("Okay, now enable remapping on the following new device(s):\n")
                            print_device_list(new_devices)
            except OSError:
                if isinstance(waitable, InputDevice):
                    remove_device(devices, waitable)
                    print("Device removed: " + str(device.name))
            except KeyboardInterrupt:
                print("Received an interrupt, exiting.")
                break
    finally:
        for device in devices:
            try:
                device.ungrab()
            except OSError as e:
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
    try:
        device.ungrab()
    except OSError as e:
        pass

