#!/usr/bin/env python

from setuptools import setup

setup(name             = "xkeysnail",
      version          = "0.0.3",
      author           = "Masafumi Oyamada",
      url              = "https://github.com/mooz/xkeysnail",
      description      = "Yet another keyboard remapping tool for X environment.",
      packages         = ["xkeysnail"],
      scripts          = ["bin/xkeysnail"],
      license          = "GPL",
      install_requires = ["evdev", "python-xlib"]
      )
