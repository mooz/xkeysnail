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
    if len(modifier_strs):
        return Combo(create_modifiers_from_strings(modifier_strs), key)
    else:
        return key

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


_GLOBAL_MAP = {
    K("C-b"): with_mark(K("left")),
    K("C-f"): with_mark(K("right")),
    K("C-p"): with_mark(K("up")),
    K("C-n"): with_mark(K("down")),
    K("C-h"): with_mark(K("backspace")),

    K("M-b"): with_mark(K("C-left")),
    K("M-f"): with_mark(K("C-right")),

    K("C-a"): with_mark(K("home")),
    K("C-e"): with_mark(K("end")),

    K("M-v"): with_mark(K("page_up")),
    K("C-v"): with_mark(K("page_down")),

    K("M-Shift-comma"): with_mark(K("C-home")),
    K("M-Shift-dot"): with_mark(K("C-end")),

    K("C-m"): K("enter"),
    K("C-j"): K("enter"),
    K("C-o"): [K("enter"), K("left")],

    K("C-w"): [K("C-x"), set_mark(False)],
    K("M-w"): [K("C-c"), set_mark(False)],
    K("C-y"): [K("C-v"), set_mark(False)],

    K("C-d"): [K("delete"), set_mark(False)],
    K("M-d"): [K("C-delete"), set_mark(False)],

    K("C-k"): [K("Shift-end"), K("C-x"), set_mark(False)],

    K("C-slash"): [K("C-z"), set_mark(False)],

    K("C-space"): set_mark(True),

    K("C-s"): K("F3"),
    K("C-r"): K("Shift-F3"),
    K("M-Shift-key_5"): K("C-h"),

    K("C-g"): [K("esc"), set_mark(False)],

    # second keymap
    K("C-x"): Mode.CONTROL_X,
    K("C-q"): Mode.CONTROL_Q,

    # next/previous tab
    K("C-M-j"): K("C-TAB"),
    K("C-M-k"): K("C-Shift-TAB"),
}

_CONTROL_X_MAP = {
    # C-x h (select all)
    Combo(None, K("h")): [K("C-home"), K("C-a"), set_mark(True), Mode.GLOBAL],
    # C-x C-f (open)
    K("C-f"): [K("C-o"), Mode.GLOBAL],
    # C-x C-s (save)
    K("C-s"): [K("C-s"), Mode.GLOBAL],
    # C-x k (kill tab)
    Combo(None, K("k")): [K("C-f4"), Mode.GLOBAL],
    # C-x C-c (exit)
    K("C-c"): [K("M-f4"), Mode.GLOBAL],
    # cancel
    K("C-g"): Mode.GLOBAL,
    # C-x u (undo)
    Combo(None, K("u")): [K("C-z"), set_mark(False)],
}

_CONTROL_Q_MAP = {}

_mode_map = _GLOBAL_MAP

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
    wm_class = get_active_window_wm_class()
    non_target_classes = ("Emacs", "URxvt")

    global _mode_map
    combo = Combo(get_pressed_modifiers(), key)
    if ((wm_class in non_target_classes) \
        or (_mode_map is _GLOBAL_MAP and combo not in _mode_map)):
        # Pass through keys
        send_key_action(key, action)
        return
    if _mode_map is _CONTROL_Q_MAP:
        send_key_action(key, action)
    if combo not in _mode_map:
        _mode_map = _GLOBAL_MAP
        return

    values = _mode_map[combo]
    if not isinstance(values, list):
        values = [values]
    for value in values:
        if callable(value):
            value = value()
            if value is None:
                continue
        if isinstance(value, Key):
            send_key(value)
        elif isinstance(value, Combo):
            send_combo(value)
        elif isinstance(value, Mode):
            _mode_map = value.get_map()
