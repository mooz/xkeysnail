from evdev import ecodes, InputDevice, list_devices
from select import select
from sys import exit
from .transform import on_event

__author__ = 'zh'


def select_device():
    """Select a device from the list of accessible input devices."""

    devices = [InputDevice(device_fn) for device_fn in reversed(list_devices())]
    if not devices:
        print('error: no input devices found (do you have rw permission on /dev/input/*?)')
        exit(1)

    # Filter out non-keyboard devices (TODO: Make it more robust)
    import re
    devices = [device for device in devices
               if re.search("keyboard", device.name, re.IGNORECASE)]

    device_format = '{0:<3} {1.fn:<20} {1.name:<35} {1.phys}'
    device_lines = [device_format.format(n, d) for n, d in enumerate(devices)]

    print('ID  {:<20} {:<35} {}'.format('Device', 'Name', 'Phys'))
    print('-' * len(max(device_lines, key=len)))
    print('\n'.join(device_lines))
    print('')

    if len(device_lines) == 1:
        return devices[0]
    else:
        choice = input('Select device [0-{}]:'.format(len(device_lines) - 1))
        return devices[int(choice)]


def loop(device):
    try:
        device.grab()
    except IOError:
        print("IOError when grabbing device")
        exit(1)
    try:
        while True:
            select([device], [], [])
            for event in device.read():
                if event.type == ecodes.EV_KEY:
                    on_event(event)
    finally:
        device.ungrab()
