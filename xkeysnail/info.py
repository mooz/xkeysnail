# -*- coding: utf-8 -*-

__name__ = "xkeysnail"
__author__ = 'zh'
__version__ = "0.4.57"
__logo__ = """
██╗  ██╗██╗  ██╗███████╗██╗   ██╗
╚██╗██╔╝██║ ██╔╝██╔════╝╚██╗ ██╔╝
 ╚███╔╝ █████╔╝ █████╗   ╚████╔╝
 ██╔██╗ ██╔═██╗ ██╔══╝    ╚██╔╝
██╔╝ ██╗██║  ██╗███████╗   ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝
  ███████╗███╗   ██╗ █████╗ ██╗██╗
  ██╔════╝████╗  ██║██╔══██╗██║██║
  ███████╗██╔██╗ ██║███████║██║██║
  ╚════██║██║╚██╗██║██╔══██║██║██║
  ███████║██║ ╚████║██║  ██║██║███████╗
  ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚══════╝
"""
__description__ = "Keyboard remapping tool for X environment."
__doc__ = """
``xkeysnail`` is a keyboard remapping tool for X environment.
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
