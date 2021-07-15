#!/usr/bin/env python

from setuptools import setup

__doc__ = None
__version__ = None
__description__ = None

exec(open("xkeysnail/info.py").read())

setup(
    name="xkeysnail",
    version=__version__,  # pylint: disable=undefined-variable
    author="Masafumi Oyamada",
    url="https://github.com/mooz/xkeysnail",
    description=__description__,  # pylint: disable=undefined-variable
    long_description=__doc__,
    packages=["xkeysnail"],
    scripts=["bin/xkeysnail"],
    license="GPL",
    dependency_links=[
        "https://github.com/luizoti/python-evdev/tarball/master#egg=python-evdev-1.4.1",
    ],
    install_requires=[
        "python-evdev==1.4.1",
        "python-xlib",
        "inotify_simple",
        "psutil"
    ],
)
