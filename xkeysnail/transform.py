from enum import Enum
from .key import Action, Combo, Key, Modifier
from .output import send_combo, send_key_action, send_key

__author__ = 'zh'

# ============================================================ #

import Xlib.display
def get_active_window_wm_class(display=Xlib.display.Display()):
    """Get active window's WM_CLASS"""
    current_window = display.get_input_focus().focus
    pair = get_class_name(current_window)
    if pair:
        # (process name, class name)
        return pair[1]
    else:
        return None

def get_class_name(window):
    """Get window's class name (recursively checks parents)"""
    try:
        wmname = window.get_wm_name()
        wmclass = window.get_wm_class()
        if wmclass is None and wmname is None:
            parent_window = window.query_tree().parent
            if parent_window:
                return get_class_name(parent_window)
            return None
        return wmclass
    except:
        return None

# ============================================================ #

_pressed_modifier_keys = set()


def update_pressed_modifier_keys(key, action):
    if action.is_pressed():
        _pressed_modifier_keys.add(key)
    else:
        _pressed_modifier_keys.discard(key)


def get_pressed_modifiers():
    return {Modifier.from_key(key) for key in _pressed_modifier_keys}


class Mode(Enum):

    GLOBAL, CONTROL_X, CONTROL_Q = range(3)

    def get_map(self):
        return {
            Mode.GLOBAL: _GLOBAL_MAP,
            Mode.CONTROL_X: _CONTROL_X_MAP,
            Mode.CONTROL_Q: _CONTROL_Q_MAP
        }[self]


# ============================================================ #
# Mark
# ============================================================ #

_mark_set = False


def with_mark(combo):
    if isinstance(combo, Key):
        combo = Combo(None, combo)

    def _with_mark():
        return combo.with_modifier(Modifier.SHIFT) if _mark_set else combo

    return _with_mark


def set_mark(mark_set):
    def _set_mark():
        global _mark_set
        _mark_set = mark_set
    return _set_mark

# ============================================================ #

def K(exp):
    "Helper function to specify keymap"
    import re
    modifier_strs = []
    while True:
        m = re.match(r"\A(C|Ctrl|M|Alt|Shift|Super|Win)-", exp)
        if m is None:
            break
        modifier = m.group(1)
        modifier_strs.append(modifier)
        exp = re.sub(r"\A{}-".format(modifier), "", exp)
    key_str = exp.upper()
    key = getattr(Key, key_str)
    return Combo(create_modifiers_from_strings(modifier_strs), key)

def create_modifiers_from_strings(modifier_strs):
    modifiers = set()
    for modifier_str in modifier_strs:
        if modifier_str == 'C' or modifier_str == 'Ctrl':
            modifiers.add(Modifier.CONTROL)
        elif modifier_str == 'M' or modifier_str == 'Alt':
            modifiers.add(Modifier.ALT)
        elif modifier_str == 'Super' or modifier_str == 'Win':
            modifiers.add(Modifier.SUPER)
            pass
        elif modifier_str == 'Shift':
            modifiers.add(Modifier.SHIFT)
    return modifiers

# ============================================================
# Keymap
# ============================================================

_toplevel_keymaps = []
_mode_maps = None

escape_next_key = {}
pass_through_key = {}

def define_keymap(condition, mappings, name="Anonymous keymap"):
    global _toplevel_keymaps
    _toplevel_keymaps.append((condition, mappings, name))
    return mappings


# ============================================================
# Key handler
# ============================================================


def on_event(event):
    on_key(Key(event.code), Action(event.value))


def on_key(key, action):
    if key in Modifier.get_all_keys():
        update_pressed_modifier_keys(key, action)
        send_key_action(key, action)
    elif not action.is_pressed():
        send_key_action(key, action)
    else:
        transform_key(key, action)


def transform_key(key, action):
    global _mode_maps
    global _toplevel_keymaps

    combo = Combo(get_pressed_modifiers(), key)

    if _mode_maps is escape_next_key:
        send_key_action(key, action)
        _mode_maps = None
        return

    is_top_level = False
    if _mode_maps is None:
        # Decide keymap(s)
        is_top_level =True
        _mode_maps = []
        wm_class = get_active_window_wm_class()
        print("Switch to window '{}'".format(wm_class))
        for condition, mappings, name in _toplevel_keymaps:
            if (callable(condition) and condition(wm_class)) \
               or (hasattr(condition, "search") and condition.search(wm_class)) \
               or condition is None:
                _mode_maps.append(mappings)
                print("Use keymap " + name)

    # _mode_maps: [global_map, local_1, local_2, ...]
    for mappings in _mode_maps:
        if combo not in mappings:
            continue
        # Found key in "mappings". Execute commands defined for the key.
        commands = mappings[combo]
        if not isinstance(commands, list):
            commands = [commands]
        # Execute commands
        for command in commands:
            # Function -> Use returned value as command
            if callable(command):
                command = command()
            # Key
            if isinstance(command, Key):
                send_key(command)
            # Combo
            elif isinstance(command, Combo):
                send_combo(command)
            # Go to next keymap
            elif isinstance(command, dict):
                _mode_maps = [command]
                return
            elif command is pass_through_key:
                send_key_action(key, action)
                _mode_maps = None
        _mode_maps = None
        return

    # Not found in all keymaps
    if is_top_level:
        # If it's top-level, pass through keys
        send_key_action(key, action)

    _mode_maps = None
