#!/usr/bin/env python

import os
from setuptools import setup

__doc__ = None
__name__ = None
__version__ = None
__description__ = None

exec(open("xkeysnail/info.py").read())

setup(
    name=__name__,
    version=__version__,  # pylint: disable=undefined-variable
    author=" | ".join(["Masafumi Oyamada", "Luiz Antonio Lazoti"]),
    url="https://github.com/mooz/xkeysnail",
    description=__description__,  # pylint: disable=undefined-variable
    long_description=__doc__,
    packages=["xkeysnail"],
    scripts=["bin/xkeysnail"],
    license="GPL",
    dependency_links=[
        "https://github.com/luizoti/evdev/tarball/master#egg=evdev-1.4.1",
    ],
    install_requires=[
        "evdev==1.4.1",
        "python-xlib",
        "inotify_simple",
        "psutil"
    ],
)
print()
print()
print('Running "xhost +SI:localuser:root" command to avoid Xlib.error.DisplayConnectionError.')
print()
os.system('xhost +SI:localuser:root')
