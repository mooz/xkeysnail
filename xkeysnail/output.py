# -*- coding: utf-8 -*-

from evdev import ecodes
from evdev.uinput import UInput
from .key import Action, Combo, Modifier

__author__ = 'zh'


_uinput = UInput()

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
        # until original modifer is released
        if modifier_key != str(modifier.get_key()):
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
