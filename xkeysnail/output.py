# -*- coding: utf-8 -*-

from evdev import ecodes
from evdev.uinput import UInput
from .key import Action, Combo, Modifier

__author__ = 'zh'


# Remove all buttons so udev doesn't think xkeysnail is a joystick
_keyboard_codes = ecodes.keys.keys() - ecodes.BTN

# But we want mouse buttons, so let's enumerate those and add them
# back into the set of buttons we'll watch and use
mouse_btns = {256: ['BTN_0', 'BTN_MISC'],
              257: 'BTN_1',
              258: 'BTN_2',
              259: 'BTN_3',
              260: 'BTN_4',
              261: 'BTN_5',
              262: 'BTN_6',
              263: 'BTN_7',
              264: 'BTN_8',
              265: 'BTN_9',
              272: ['BTN_LEFT', 'BTN_MOUSE'],
              274: 'BTN_MIDDLE',
              273: 'BTN_RIGHT'}
_keyboard_codes.update(mouse_btns)

_uinput = UInput(events={ecodes.EV_KEY: _keyboard_codes,
                         ecodes.EV_REL: set([0,1,6,8,9]),
                         })

_pressed_modifier_keys = set()
_pressed_keys = set()

def output_modifier_key():
    return _pressed_modifier_keys

def update_modifier_key_pressed(key, action):
    if key in Modifier.get_all_keys():
        if action.is_pressed():
            _pressed_modifier_keys.add(key)
        else:
            _pressed_modifier_keys.discard(key)

def update_pressed_keys(key, action):
    if action.is_pressed():
        _pressed_keys.add(key)
    else:
        _pressed_keys.discard(key)

def is_pressed(key):
    return key in _pressed_keys

def send_sync():
    _uinput.syn()


def send_event(event):
    _uinput.write_event(event)
    send_sync()


def send_key_action(key, action):
    update_modifier_key_pressed(key, action)
    update_pressed_keys(key, action)
    _uinput.write(ecodes.EV_KEY, key, action)
    send_sync()


def send_combo(combo):

    released_modifiers_keys = []

    extra_modifier_keys = _pressed_modifier_keys.copy()
    missing_modifiers = combo.modifiers.copy()
    for pressed_key in _pressed_modifier_keys:
        for modifier in combo.modifiers:
            if pressed_key in modifier.get_keys():
                extra_modifier_keys.remove(pressed_key)
                missing_modifiers.remove(modifier)

    for modifier_key in extra_modifier_keys:
        # Do not release new modifier
        # until original modifier is released
        # unless no modifier is the new mapping
        if len(combo.modifiers) > 0:
            for modifier in combo.modifiers:
                if modifier_key != str(modifier.get_key()):
                    send_key_action(modifier_key, Action.RELEASE)
                    released_modifiers_keys.append(modifier_key)
        else:
            send_key_action(modifier_key, Action.RELEASE)
            released_modifiers_keys.append(modifier_key)

    pressed_modifier_keys = []
    for modifier in missing_modifiers:
        modifier_key = modifier.get_key()
        send_key_action(modifier_key, Action.PRESS)
        pressed_modifier_keys.append(modifier_key)

    send_key_action(combo.key, Action.PRESS)

    send_key_action(combo.key, Action.RELEASE)

    for modifier in reversed(released_modifiers_keys):
        send_key_action(modifier, Action.PRESS)


def send_key(key):
    send_combo(Combo(None, key))
