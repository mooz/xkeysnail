from evdev import ecodes, InputDevice, list_devices
from select import select
from sys import exit
from .transform import on_event

__author__ = 'zh'


def get_devices_list():
    return [InputDevice(device_fn) for device_fn in reversed(list_devices())]


def is_keyboard_device(device):
    """Check"""
    capabilities = device.capabilities(verbose=True)
    if ('EV_KEY', 1) not in capabilities:
        return False
    if ('KEY_SPACE', 57) not in capabilities[('EV_KEY', 1)]:
        return False
    return True


def select_device():
    """Select a device from the list of accessible input devices."""
    devices = get_devices_list()
    if not devices:
        print('error: no input devices found (do you have rw permission on /dev/input/*?)')
        exit(1)

    devices = [device for device in devices
               if is_keyboard_device(device) and device.name != "py-evdev-uinput"]

    device_format = '{0:<3} {1.fn:<20} {1.name:<35} {1.phys}'
    device_lines = [device_format.format(n, d) for n, d in enumerate(devices)]

    print('ID  {:<20} {:<35} {}'.format('Device', 'Name', 'Phys'))
    print('-' * len(max(device_lines, key=len)))
    print('\n'.join(device_lines))
    print('')

    return devices


def loop(devices):
    try:
        for device in devices:
            device.grab()
    except IOError:
        print("IOError when grabbing device")
        exit(1)
    try:
        while True:
            try:
                r, w, x = select(devices, [], [])
                for device in r:
                    # device = devices[fd]
                    for event in device.read():
                        if event.type == ecodes.EV_KEY:
                            on_event(event)
            except OSError as e:
                print("Device removed: " + str(device.name))
                devices.remove(device)
    finally:
        for device in devices:
            device.ungrab()
