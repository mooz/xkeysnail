#!/usr/bin/env python

from setuptools import setup

setup(name             = "pykeymacs",
      version          = "0.0.1",
      author           = "zh",
      url              = "https://github.com/DreaminginCodeZH/pykeymacs",
      description      = "Emacs style keyboard macros implemented in Python, using evdev and uinput.",
      packages         = ["pykeymacs"],
      scripts          = ["bin/pykeymacs"],
      license          = "GPL",
      install_requires = ["evdev", "python-xlib"]
      )
