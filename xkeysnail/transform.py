# -*- coding: utf-8 -*-

import itertools
from time import time
from inspect import signature
from .key import Action, Combo, Key, Modifier
from .output import send_combo, send_key_action, send_key, is_pressed, output_modifier_key

__author__ = 'zh'

# ============================================================ #

import Xlib.display

_release_combo = False

def get_active_window_wm_class(display=Xlib.display.Display()):
    """Get active window's WM_CLASS"""
    current_window = display.get_input_focus().focus
    pair = get_class_name(current_window)
    if pair:
        # (process name, class name)
        return str(pair[1])
    else:
        return ""


def get_class_name(window):
    """Get window's class name (recursively checks parents)"""
    try:
        wmname = window.get_wm_name()
        wmclass = window.get_wm_class()
        # workaround for Java app
        # https://github.com/JetBrains/jdk8u_jdk/blob/master/src/solaris/classes/sun/awt/X11/XFocusProxyWindow.java#L35
        if (wmclass is None and wmname is None) or "FocusProxy" in wmclass:
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


# ============================================================ #


_pressed_keys = set()


def update_pressed_keys(key, action):
    if action.is_pressed():
        _pressed_keys.add(key)
    else:
        _pressed_keys.discard(key)


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


def with_or_set_mark(combo):
    if isinstance(combo, Key):
        combo = Combo(None, combo)

    def _with_or_set_mark():
        global _mark_set
        _mark_set = True
        return combo.with_modifier(Modifier.SHIFT)

    return _with_or_set_mark


# ============================================================ #
# Utility functions for keymap
# ============================================================ #


def launch(command):
    """Launch command"""
    def launcher():
        from subprocess import Popen
        Popen(command)
    return launcher


def sleep(sec):
    """Sleep sec in commands"""
    def sleeper():
        import time
        time.sleep(sec)
    return sleeper

# ============================================================ #


def K(exp):
    "Helper function to specify keymap"
    import re
    modifier_strs = []
    while True:
        m = re.match(r"\A(LC|LCtrl|RC|RCtrl|C|Ctrl|LM|LAlt|RM|RAlt|M|Alt|LShift|RShift|Shift|LSuper|LWin|RSuper|RWin|Super|Win)-", exp)
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
        if modifier_str == 'LC' or modifier_str == 'LCtrl':
            modifiers.add(Modifier.L_CONTROL)
        elif modifier_str == 'RC' or modifier_str == 'RCtrl':
            modifiers.add(Modifier.R_CONTROL)
        elif modifier_str == 'C' or modifier_str == 'Ctrl':
            modifiers.add(Modifier.CONTROL)
        elif modifier_str == 'LM' or modifier_str == 'LAlt':
            modifiers.add(Modifier.L_ALT)
        elif modifier_str == 'RM' or modifier_str == 'RAlt':
            modifiers.add(Modifier.R_ALT)
        elif modifier_str == 'M' or modifier_str == 'Alt':
            modifiers.add(Modifier.ALT)
        elif modifier_str == 'LSuper' or modifier_str == 'LWin':
            modifiers.add(Modifier.L_SUPER)
            pass
        elif modifier_str == 'RSuper' or modifier_str == 'RWin':
            modifiers.add(Modifier.R_SUPER)
            pass
        elif modifier_str == 'Super' or modifier_str == 'Win':
            modifiers.add(Modifier.SUPER)
            pass
        elif modifier_str == 'LShift':
            modifiers.add(Modifier.L_SHIFT)
        elif modifier_str == 'RShift':
            modifiers.add(Modifier.R_SHIFT)
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

    # Expand not L/R-specified modifiers
    # Suppose a nesting is not so deep
    # {K("C-a"): Key.A,
    #  K("C-b"): {
    #      K("LC-c"): Key.B,
    #      K("C-d"): Key.C}}
    # ->
    # {K("LC-a"): Key.A, K("RC-a"): Key.A,
    #  K("LC-b"): {
    #      K("LC-c"): Key.B,
    #      K("LC-d"): Key.C,
    #      K("RC-d"): Key.C},
    #  K("RC-b"): {
    #      K("LC-c"): Key.B,
    #      K("LC-d"): Key.C,
    #      K("RC-d"): Key.C}}
    def expand(target):
        if isinstance(target, dict):
            expanded_mappings = {}
            keys_for_deletion = []
            for k, v in target.items():
                # Expand children
                expand(v)

                if isinstance(k, Combo):
                    expanded_modifiers = []
                    for modifier in k.modifiers:
                        if not modifier.is_specified():
                            expanded_modifiers.append([modifier.to_left(), modifier.to_right()])
                        else:
                            expanded_modifiers.append([modifier])

                    # Create a Cartesian product of expanded modifiers
                    expanded_modifier_lists = itertools.product(*expanded_modifiers)
                    # Create expanded mappings
                    for modifiers in expanded_modifier_lists:
                        expanded_mappings[Combo(set(modifiers), k.key)] = v
                    keys_for_deletion.append(k)

            # Delete original mappings whose key was expanded into expanded_mappings
            for key in keys_for_deletion:
                del target[key]
            # Merge expanded mappings into original mappings
            target.update(expanded_mappings)

    expand(mappings)

    _toplevel_keymaps.append((condition, mappings, name))
    return mappings


# ============================================================
# Key handler
# ============================================================

# keycode translation
# e.g., { Key.CAPSLOCK: Key.LEFT_CTRL }
_mod_map = None
_conditional_mod_map = []

# multipurpose keys
# e.g, {Key.LEFT_CTRL: [Key.ESC, Key.LEFT_CTRL, Action.RELEASE]}
_multipurpose_map = None
_conditional_multipurpose_map = []

# last key that sent a PRESS event or a non-mod or non-multi key that sent a RELEASE
# or REPEAT
_last_key = None

# last key time record time when execute multi press
_last_key_time = time()
_timeout = 1
def define_timeout(seconds=1):
    global _timeout
    _timeout = seconds



def define_modmap(mod_remappings):
    """Defines modmap (keycode translation)

    Example:

    define_modmap({
        Key.CAPSLOCK: Key.LEFT_CTRL
    })
    """
    global _mod_map
    _mod_map = mod_remappings


def define_conditional_modmap(condition, mod_remappings):
    """Defines conditional modmap (keycode translation)

    Example:

    define_conditional_modmap(re.compile(r'Emacs'), {
        Key.CAPSLOCK: Key.LEFT_CTRL
    })
    """
    if hasattr(condition, 'search'):
        condition = condition.search
    if not callable(condition):
        raise ValueError('condition must be a function or compiled regexp')
    _conditional_mod_map.append((condition, mod_remappings))


def define_multipurpose_modmap(multipurpose_remappings):
    """Defines multipurpose modmap (multi-key translations)

    Give a key two different meanings. One when pressed and released alone and
    one when it's held down together with another key (making it a modifier
    key).

    Example:

    define_multipurpose_modmap(
        {Key.CAPSLOCK: [Key.ESC, Key.LEFT_CTRL]
    })
    """
    global _multipurpose_map
    for key, value in multipurpose_remappings.items():
        value.append(Action.RELEASE)
    _multipurpose_map = multipurpose_remappings


def define_conditional_multipurpose_modmap(condition, multipurpose_remappings):
    """Defines conditional multipurpose modmap (multi-key translation)

    Example:

    define_conditional_multipurpose_modmap(lambda wm_class, device_name: device_name.startswith("Microsoft"), {
        {Key.CAPSLOCK: [Key.ESC, Key.LEFT_CTRL]
    })
    """
    if hasattr(condition, 'search'):
        condition = condition.search
    if not callable(condition):
        raise ValueError('condition must be a function or compiled regexp')
    for key, value in multipurpose_remappings.items():
        value.append(Action.RELEASE)
    _conditional_multipurpose_map.append((condition, multipurpose_remappings))


def multipurpose_handler(multipurpose_map, key, action):

    def maybe_press_modifiers(multipurpose_map):
        """Search the multipurpose map for keys that are pressed. If found and
        we have not yet sent it's modifier translation we do so."""
        for k, [ _, mod_key, state ] in multipurpose_map.items():
            if k in _pressed_keys and mod_key not in _pressed_modifier_keys:
                on_key(mod_key, Action.PRESS)

    # we need to register the last key presses so we know if a multipurpose key
    # was a single press and release
    global _last_key
    global _last_key_time

    if key in multipurpose_map:
        single_key, mod_key, key_state = multipurpose_map[key]
        key_is_down = key in _pressed_keys
        mod_is_down = mod_key in _pressed_modifier_keys
        key_was_last_press = key == _last_key

        update_pressed_keys(key, action)
        if action == Action.RELEASE and key_is_down:
            # it is a single press and release
            if key_was_last_press and _last_key_time + _timeout > time():
                maybe_press_modifiers(multipurpose_map)  # maybe other multipurpose keys are down
                on_key(single_key, Action.PRESS)
                on_key(single_key, Action.RELEASE)
            # it is the modifier in a combo
            elif mod_is_down:
                on_key(mod_key, Action.RELEASE)
        elif action == Action.PRESS and not key_is_down:
            _last_key_time = time()
    # if key is not a multipurpose or mod key we want eventual modifiers down
    elif (key not in Modifier.get_all_keys()) and action == Action.PRESS:
        maybe_press_modifiers(multipurpose_map)

    # we want to register all key-presses
    if action == Action.PRESS:
        _last_key = key


def on_event(event, device_name, quiet):
    key = Key(event.code)
    action = Action(event.value)
    wm_class = None
    # translate keycode (like xmodmap)
    active_mod_map = _mod_map
    if _conditional_mod_map:
        wm_class = get_active_window_wm_class()
        for condition, mod_map in _conditional_mod_map:
            params = [wm_class]
            if len(signature(condition).parameters) == 2:
                params = [wm_class, device_name]

            if condition(*params):
                active_mod_map = mod_map
                break
    if active_mod_map and key in active_mod_map:
        key = active_mod_map[key]

    active_multipurpose_map = _multipurpose_map
    if _conditional_multipurpose_map:
        wm_class = get_active_window_wm_class()
        for condition, mod_map in _conditional_multipurpose_map:
            params = [wm_class]
            if len(signature(condition).parameters) == 2:
                params = [wm_class, device_name]

            if condition(*params):
                active_multipurpose_map = mod_map
                break
    if active_multipurpose_map:
        multipurpose_handler(active_multipurpose_map, key, action)
        if key in active_multipurpose_map:
            return

    on_key(key, action, wm_class=wm_class, quiet=quiet)
    update_pressed_keys(key, action)


def on_key(key, action, wm_class=None, quiet=False):
    global _release_combo
    output_mods = output_modifier_key().copy()
    if key in Modifier.get_all_keys():
        update_pressed_modifier_keys(key, action)
        send_key_action(key, action)
        # Release mapped modifier only when physical mod
        # is released
        if str(key) != "Key.LEFT_SHIFT" and str(key) != "Key.RIGHT_SHIFT":
            for output_key in output_mods:
                update_pressed_modifier_keys(output_key, action)
                send_key_action(output_key, action)
    elif not action.is_pressed():
        if is_pressed(key):
            send_key_action(key, action)
        # Unset modifiers used in nested mode_maps
        elif _release_combo and len(output_mods) > 0:
            _release_combo = False
            for output_key in output_mods:
                update_pressed_modifier_keys(output_key, action)
                send_key_action(output_key, action)
    else:
        transform_key(key, action, wm_class=wm_class, quiet=quiet)
    # Will unset mode maps modifiers on next combo
    if _mode_maps != None:
        _release_combo = True


def transform_key(key, action, wm_class=None, quiet=False):
    global _mode_maps
    global _toplevel_keymaps

    combo = Combo(get_pressed_modifiers(), key)

    if _mode_maps is escape_next_key:
        print("Escape key: {}".format(combo))
        send_key_action(key, action)
        _mode_maps = None
        return

    is_top_level = False
    if _mode_maps is None:
        # Decide keymap(s)
        is_top_level = True
        _mode_maps = []
        if wm_class is None:
            wm_class = get_active_window_wm_class()
        keymap_names = []
        for condition, mappings, name in _toplevel_keymaps:
            if (callable(condition) and condition(wm_class)) \
               or (hasattr(condition, "search") and condition.search(wm_class)) \
               or condition is None:
                _mode_maps.append(mappings)
                keymap_names.append(name)
        if not quiet:
            print("WM_CLASS '{}' | active keymaps = [{}]".format(wm_class, ", ".join(keymap_names)))

    if not quiet:
        print(combo)

    # _mode_maps: [global_map, local_1, local_2, ...]
    for mappings in _mode_maps:
        if combo not in mappings:
            continue
        # Found key in "mappings". Execute commands defined for the key.
        reset_mode = handle_commands(mappings[combo], key, action)
        if reset_mode:
            _mode_maps = None
        return

    # Not found in all keymaps
    if is_top_level:
        # If it's top-level, pass through keys
        send_key_action(key, action)

    _mode_maps = None


def handle_commands(commands, key, action):
    """
    returns: reset_mode (True/False) if this is True, _mode_maps will be reset
    """
    global _mode_maps

    if not isinstance(commands, list):
        commands = [commands]

    # Execute commands
    for command in commands:
        if callable(command):
            reset_mode = handle_commands(command(), key, action)
            if reset_mode:
                return True

        if isinstance(command, Key):
            send_key(command)
        elif isinstance(command, Combo):
            send_combo(command)
        elif command is escape_next_key:
            _mode_maps = escape_next_key
            return False
        # Go to next keymap
        elif isinstance(command, dict):
            _mode_maps = [command]
            return False
        elif command is pass_through_key:
            send_key_action(key, action)
            return True
    # Reset keymap in ordinary flow
    return True
