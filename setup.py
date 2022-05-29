#!/usr/bin/env python
# pylint: disable=undefined-variable

import os
from setuptools import setup


__doc__ = """
``keyscrew`` is a keyboard remapping tool.
It's like ``xmodmap`` but allows more flexible remappings.

-  Has high-level and flexible remapping mechanisms, such as

   -  **per-application keybindings can be defined**
   -  **per-device keybindings can be defined**
   -  **multiple stroke keybindings can be defined** such as
      ``Ctrl+x Ctrl+c`` to ``Ctrl+q``
   -  **not only key remapping but arbitrary commands defined by
      Python can be bound to a key**

-  Runs in low-level layer (``evdev`` and ``uinput``), making
   **remapping work in almost all the places**
"""

setup(
    name='keyscrew',
    version='0.4.81',
    author=' | '.join(['Masafumi Oyamada', 'Luiz Antonio Lazoti', 'zh']),
    url='https://github.com/luizoti/keyscrew',
    description='Keyboard remapping tool.',
    long_description=__doc__,
    packages=['keyscrew'],
    scripts=['bin/keyscrew'],
    license='GPL',
)

print()
print()
print('Running "xhost +SI:localuser:root" command to avoid Xlib.error.DisplayConnectionError.')
print()
os.system('xhost +SI:localuser:root')
