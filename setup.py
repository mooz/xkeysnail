#!/usr/bin/env python

from setuptools import setup
exec(open("xkeysnail/info.py").read())

setup(name             = "xkeysnail",
      version          = __version__,
      author           = "Masafumi Oyamada",
      url              = "https://github.com/mooz/xkeysnail",
      description      = __description__,
      long_description = __doc__,
      packages         = ["xkeysnail"],
      scripts          = ["bin/xkeysnail"],
      license          = "GPL",
      install_requires = ["evdev", "python-xlib", "inotify_simple", "appdirs"]
      )
