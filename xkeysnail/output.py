# -*- coding: utf-8 -*-

from evdev import ecodes
from evdev.uinput import UInput
from .key import Action, Combo, Modifier

__author__ = 'zh'


_uinput = UInput()

_pressed_modifier_keys = set()


def update_modifier_key_pressed(key, action):
    if key in Modifier.get_all_keys():
        if action.is_pressed():
            _pressed_modifier_keys.add(key)
        else:
            _pressed_modifier_keys.discard(key)


def send_sync():
    _uinput.syn()


def send_event(event):
    _uinput.write_event(event)
    send_sync()


def send_key_action(key, action):
    update_modifier_key_pressed(key, action)
    _uinput.write(ecodes.EV_KEY, key, action)
    send_sync()


def send_combo(combo):

    released_modifiers_keys = []
    for modifier in set(Modifier) - combo.modifiers:
        for modifier_key in modifier.get_keys():
            if modifier_key in _pressed_modifier_keys:
                send_key_action(modifier_key, Action.RELEASE)
                released_modifiers_keys.append(modifier_key)

    pressed_modifier_keys = []
    for modifier in combo.modifiers:
        if not any(modifier_key in _pressed_modifier_keys for modifier_key in modifier.get_keys()):
            modifier_key = modifier.get_key()
            send_key_action(modifier_key, Action.PRESS)
            pressed_modifier_keys.append(modifier_key)

    send_key_action(combo.key, Action.PRESS)

    send_key_action(combo.key, Action.RELEASE)

    for modifier in reversed(pressed_modifier_keys):
        send_key_action(modifier, Action.RELEASE)

    for modifier in reversed(released_modifiers_keys):
        send_key_action(modifier, Action.PRESS)


def send_key(key):
    send_combo(Combo(None, key))
