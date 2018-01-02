# xkeysnail

`xkeysnail` is a yet another keyboard remapping tool for X environment. It's
like `xmodmap` but allows more flexible remappings.

- **Pros**
  - Has high-level and flexible remapping mechanisms, such as
    - **per-application keymaps**
    - **multiple stroke keybindings**
    - **arbitrary commands defined by Python**
  - Runs in low-level layer (`evdev` and `uinput`), making **remapping work in almost all the places**
- **Cons**
  - Runs in root-mode (requires `sudo`)

The key remapping mechanism of `xkeysnail` is based on `pykeymacs`
(https://github.com/DreaminginCodeZH/pykeymacs).

## Installation

Requires root privilege and Python 3.

### Ubuntu

    sudo apt install python3-pip
    sudo pip install xkeysnail

### From source

    git clone --depth 1 https://github.com/mooz/xkeysnail.git
    cd xkeysnail
    sudo pip install --upgrade .
    
## Usage

    sudo xkeysnail config.py

## How to prepare `config.py`?

(**If you just need Emacs-like keybindings, consider to
use
[`example/config.py`](https://github.com/mooz/xkeysnail/blob/master/example/config.py),
which contains Emacs-like keybindings)**.

Configuration file is a Python script that consists of several keymaps defined
by `define_keymap(condition, mappings, name)`, which specify remappings on each
application.

`define_keymap(condition, mappings, name)` defines a keymap consists of
`mappings`, which is activated when the `condition` is satisfied.

1. `condition`: one of the followings
  - Regular expression (e.g., `re.compile("YYY")`)
    - Activates the `mappings` if the pattern `YYY` matches the `WM_CLASS` of
      the application.
  - `lambda wm_class: some_condition(wm_class)`
    - Activates the `mappings` if the `WM_CLASS` of the application satisfies
      the condition specified by the `lambda` function.
2. `mappings`: dictionary (`{key: command, key2: command2, ...}`)
  - `key`: Key to override specified by `K("YYY")`
  - `command`: one of the followings
    - `K("YYY")`: Dispatch custom key to the application.
    - `None`: Pass through `key` to the application. Useful to override the
      global mappings behavior on certain applications.
    - `[command1, command2, ...]`: Execute commands sequentially.
    - `function`: Execute the function and use the return value as command.
    - `dictionary`: Sub-keymap. Used to define multiple stroke keybindings.
3. `name`: keymap name. optional.

To check `WM_CLASS` of the application you want to have custom keymap, use
`xprop` command:

    xprop WM_CLASS

and then click the application. `xprop` tells `WM_CLASS` of the application as follows.

    WM_CLASS(STRING) = "Navigator", "Firefox"

Use the second value (in this case `Firefox`) as the `WM_CLASS` value in your
`config.py`.

### Examples

```python
import re
from pykeymacs.transform import K, define_keymap, with_mark, set_mark, escape_next_key

define_keymap(re.compile("Firefox|Google-chrome"), {
    K("C-M-j"): K("C-TAB"),
    K("C-M-k"): K("C-Shift-TAB"),
}, "Firefox and Chrome")

# Emacs-like keybindings
define_keymap(lambda wm_class: wm_class not in ("Emacs", "URxvt"), {
    # Cursor
    K("C-b"): with_mark(K("left")),
    K("C-f"): with_mark(K("right")),
    K("C-p"): with_mark(K("up")),
    K("C-n"): with_mark(K("down")),
    K("C-h"): with_mark(K("backspace")),
    # Forward/Backward word
    K("M-b"): with_mark(K("C-left")),
    K("M-f"): with_mark(K("C-right")),
    # Beginning/End of line
    K("C-a"): with_mark(K("home")),
    K("C-e"): with_mark(K("end")),
    # Page up/down
    K("M-v"): with_mark(K("page_up")),
    K("C-v"): with_mark(K("page_down")),
    # Beginning/End of file
    K("M-Shift-comma"): with_mark(K("C-home")),
    K("M-Shift-dot"): with_mark(K("C-end")),
    # Newline
    K("C-m"): K("enter"),
    K("C-j"): K("enter"),
    K("C-o"): [K("enter"), K("left")],
    # Copy
    K("C-w"): [K("C-x"), set_mark(False)],
    K("M-w"): [K("C-c"), set_mark(False)],
    K("C-y"): [K("C-v"), set_mark(False)],
    # Delete
    [M S2]K("C-d"): [K("delete"), set_mark(False)],
    K("M-d"): [K("C-delete"), set_mark(False)],
    # Kill line
    K("C-k"): [K("Shift-end"), K("C-x"), set_mark(False)],
    # Undo
    K("C-slash"): [K("C-z"), set_mark(False)],
    K("C-Shift-ro"): K("C-z"),
    # Mark
    K("C-space"): set_mark(True),
    # Search
    K("C-s"): K("F3"),
    K("C-r"): K("Shift-F3"),
    K("M-Shift-key_5"): K("C-h"),
    # Cancel
    K("C-g"): [K("esc"), set_mark(False)],
    # Escape
    K("C-q"): escape_next_key,
    # C-x YYY
    K("C-x"): {
        # C-x h (select all)
        K("h"): [K("C-home"), K("C-a"), set_mark(True)],
        # C-x C-f (open)
        K("C-f"): [K("C-o")],
        # C-x C-s (save)
        K("C-s"): [K("C-s")],
        # C-x k (kill tab)
        K("k"): [K("C-f4")],
        # C-x C-c (exit)
        K("C-c"): [K("M-f4")],
        # cancel
        K("C-g"): None,
        # C-x u (undo)
        K("u"): [K("C-z"), set_mark(False)],
    }
}, "Emacs-like keys")
```

## License

`xkeysnail` is distributed under GPL.

    xkeysnail
    Copyright (C) 2018 Masafumi Oyamada

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

`xkeysnail` is based on `pykeymacs`
 (https://github.com/DreaminginCodeZH/pykeymacs), which is distributed under
 GPL.

    pykeymacs
    Copyright (C) 2015 Zhang Hai

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
