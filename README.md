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
by `define_keymap(condition, mappings, name)`

### `define_keymap(condition, mappings, name)`

Defines a keymap consists of `mappings`, which is activated when the `condition`
is satisfied.

Argument `condition` specifies the condition of activating the `mappings` on an
application and takes one of the following forms:
- Regular expression (e.g., `re.compile("YYY")`)
  - Activates the `mappings` if the pattern `YYY` matches the `WM_CLASS` of
    the application.
- `lambda wm_class: some_condition(wm_class)`
  - Activates the `mappings` if the `WM_CLASS` of the application satisfies
    the condition specified by the `lambda` function.
- `None`: Refers to no condition. `None`-specified keymap will be a global
  keymap and is always enabled.

Argument `mappings` is a dictionary in the form of `{key: command, key2:
command2, ...}` where `key` and `command` take following forms:
- `key`: Key to override specified by `K("YYY")`
  - For the syntax of key specification, please refer to
    the [key specification section](#key-specification).
- `command`: one of the followings
  - `K("YYY")`: Dispatch custom key to the application.
  - `[command1, command2, ...]`: Execute commands sequentially.
  - `{ ... }`: Sub-keymap. Used to define multiple stroke keybindings.
    See [multiple stroke keys](#multiple-stroke-keys) for details.
  - `pass_through_key`: Pass through `key` to the application. Useful to
    override the global mappings behavior on certain applications.
  - `escape_next_key`: Escape next key.
  - arbitrary function: The function is executed and the returned value is used
    as a command.
    - Can be used to invoke UNIX commands.

Argument `name` specifies the keymap name. This is an optional argument.

#### Key Specification

Key specification in a keymap is in a form of `K("(<Modifier>-)*<Key>")` where

`<Modifier>` is mone of the followings
- `C` or `Ctrl` -> Control key
- `M` or `Alt` -> Alt key
- `Shift` -> Shift key
- `Super` or `Win` -> Super/Windows key

and `<Key>` is a key whose name is defined
in [`key.py`](https://github.com/mooz/xkeysnail/blob/master/xkeysnail/key.py).

Here is a list of key specification examples:

- `K("C-M-j")`: `Ctrl` + `Alt` + `j`
- `K("Ctrl-m")`: `Ctrl` + `m`
- `K("Win-o")`: `Super/Windows` + `o`
- `K("M-Shift-comma")`: `Alt` + `Shift` + `comma` (= `Alt` + `>`)

#### Multiple stroke keys

When you needs multiple stroke keys, define nested keymap. For example, the
following example remaps `C-x C-c` to `C-q`.

```python
define_keymap(None, {
    K("C-x"): {
      K("C-c"): K("C-q"),
      K("C-f"): K("C-q"),
    }
})
```

#### Checking an application's `WM_CLASS` with `xprop`

To check `WM_CLASS` of the application you want to have custom keymap, use
`xprop` command:

    xprop WM_CLASS

and then click the application. `xprop` tells `WM_CLASS` of the application as follows.

    WM_CLASS(STRING) = "Navigator", "Firefox"

Use the second value (in this case `Firefox`) as the `WM_CLASS` value in your
`config.py`.

### Example `config.py`

See [`example/config.py`](https://github.com/mooz/xkeysnail/blob/master/example/config.py).

Here is an excerpt of `example/config.py`.

```python
from xkeysnail.transform import *

define_keymap(re.compile("Firefox|Google-chrome"), {
    # Ctrl+Alt+j/k to switch next/previous tab
    K("C-M-j"): K("C-TAB"),
    K("C-M-k"): K("C-Shift-TAB"),
}, "Firefox and Chrome")

define_keymap(re.compile("Zeal"), {
    # Ctrl+s to focus search area
    K("C-s"): K("C-k"),
}, "Zeal")

define_keymap(lambda wm_class: wm_class not in ("Emacs", "URxvt"), {
    # Cancel
    K("C-g"): [K("esc"), set_mark(False)],
    # Escape
    K("C-q"): escape_next_key,
    # C-x YYY
    K("C-x"): {
        # C-x h (select all)
        K("h"): [K("C-home"), K("C-a"), set_mark(True)],
        # C-x C-f (open)
        K("C-f"): K("C-o"),
        # C-x C-s (save)
        K("C-s"): K("C-s"),
        # C-x k (kill tab)
        K("k"): K("C-f4"),
        # C-x C-c (exit)
        K("C-c"): K("M-f4"),
        # cancel
        K("C-g"): pass_through_key,
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
