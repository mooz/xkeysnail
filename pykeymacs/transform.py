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
    wmname = window.get_wm_name()
    wmclass = window.get_wm_class()
    if wmclass is None and wmname is None:
        parent_window = window.query_tree().parent
        if parent_window:
            return get_class_name(parent_window)
        return None
    return wmclass

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
            # modifiers.add(Modifier.SUPER)
            pass
        elif modifier_str == 'Shift':
            modifiers.add(Modifier.SHIFT)
    return modifiers


_GLOBAL_MAP = {

    K("C-b"): with_mark(Key.LEFT),
    K("C-f"): with_mark(Key.RIGHT),
    K("C-p"): with_mark(Key.UP),
    K("C-n"): with_mark(Key.DOWN),
    K("C-h"): with_mark(Key.BACKSPACE),
    K("C-m"): Key.ENTER,

    K("M-b"): with_mark(Combo(Modifier.CONTROL, Key.LEFT)),
    K("M-f"): with_mark(Combo(Modifier.CONTROL, Key.RIGHT)),

    K("C-a"): with_mark(Key.HOME),
    K("C-e"): with_mark(Key.END),

    K("M-v"): with_mark(Key.PAGE_UP),
    K("C-v"): with_mark(Key.PAGE_DOWN),

    K("M-Shift-comma"): with_mark(Combo(Modifier.CONTROL, Key.HOME)),
    K("M-Shift-dot"): with_mark(Combo(Modifier.CONTROL, Key.END)),

    K("C-j"): Key.ENTER,
    K("C-o"): [Key.ENTER, Key.LEFT],

    K("C-w"): [Combo(Modifier.CONTROL, Key.X), set_mark(False)],
    K("M-w"): [Combo(Modifier.CONTROL, Key.C), set_mark(False)],
    K("C-y"): [Combo(Modifier.CONTROL, Key.V), set_mark(False)],

    K("C-d"): [Key.DELETE, set_mark(False)],
    K("M-d"): [Combo(Modifier.CONTROL, Key.DELETE), set_mark(False)],

    K("C-k"): [Combo(Modifier.SHIFT, Key.END), Combo(Modifier.CONTROL, Key.X), set_mark(False)],

    K("C-slash"): [Combo(Modifier.CONTROL, Key.Z), set_mark(False)],

    K("C-space"): set_mark(True),

    K("C-s"): Key.F3,
    K("C-r"): Combo(Modifier.SHIFT, Key.F3),
    K("M-Shift-key_5"): Combo(Modifier.CONTROL, Key.H),

    K("C-g"): [Key.ESC, set_mark(False)],

    K("C-x"): Mode.CONTROL_X,
    K("C-q"): Mode.CONTROL_Q,

    # next/previous tab
    K("C-M-j"): Combo(Modifier.CONTROL, Key.TAB),
    K("C-M-k"): Combo({Modifier.CONTROL, Modifier.SHIFT}, Key.TAB),
}

_CONTROL_X_MAP = {

    Combo(None, Key.H): [Combo(Modifier.CONTROL, Key.HOME), Combo(Modifier.CONTROL, Key.A), set_mark(True), Mode.GLOBAL],

    Combo(Modifier.CONTROL, Key.F): [Combo(Modifier.CONTROL, Key.O), Mode.GLOBAL],

    Combo(Modifier.CONTROL, Key.S): [Combo(Modifier.CONTROL, Key.S), Mode.GLOBAL],

    Combo(None, Key.K): [Combo(Modifier.CONTROL, Key.F4), Mode.GLOBAL],
    Combo(Modifier.CONTROL, Key.C): [Combo(Modifier.ALT, Key.F4), Mode.GLOBAL],

    Combo(Modifier.CONTROL, Key.G): Mode.GLOBAL
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
