# -*- coding: utf-8 -*-
# xprop WM_CLASS

import re

from keyscrew.utils import *
from keyscrew.transform import *

WM_LIST = [
            'konsole',
            'xfce4-terminal',
            'dolphin',
            'vlc',
            'kodi',
            'ksmserver',
            'firefox',
            'brave-browser',
            'xfce4-session',
        ]


DEVICES = {
	'MSMOUSE': 'Microsoft Microsoft® 2.4GHz Transceiver v9.0',
	'BDREMOTE': 'Sony Computer Entertainment Inc BD Remote Control',
	'USBKEYBOARD': 'SIGMACHIP USB Keyboard',
}

define_keymap(DEVICES['BDREMOTE'], lambda wm_class: wm_class not in WM_LIST, {
    K("EJECTCD"):           K("Ctrl-Alt-DELETE"),
    K("KEY_AUDIO"):         K("a"),
    # K("KEY_ANGLE"):       K("Ctrl-Alt-Super-l"),
    K("KEY_SUBTITLE"):      K("l"),
    K("KEY_CLEAR"):         K("Shift-C-M-d"),
    # K("KEY_TIME"):            K("Ctrl-Alt-Super-l"),
    K("KEY_0"):             K("key_0"),
    K("KEY_1"):             K("key_1"),
    K("KEY_2"):             K("key_2"),
    K("KEY_3"):             K("key_3"),
    K("KEY_4"):             K("key_4"),
    K("KEY_5"):             K("key_5"),
    K("KEY_6"):             K("key_6"),
    K("KEY_7"):             K("key_7"),
    K("KEY_8"):             K("key_8"),
    K("KEY_9"):             K("key_9"),
    # K("KEY_RED"):           K("Ctrl-Alt-Super-l"),
    # K("KEY_GREEN"):         K("Ctrl-Alt-Super-l"),
    K("KEY_BLUE"):          [launch(["deluge-gtk &"]), sleep(1), launch(["deluge-gtk &"])],
    K("KEY_YELLOW"):        K("Super-e"),
    K("KEY_INFO"):          K("Super-p"),
    K("MENU"):              K("M-TAB"),
    # K("KEY_CONTEXT_MENU"):    K("Ctrl-Alt-Super-l"),
    K("ESC"):               K("M-f4"),
    # K("KEY_OPTION"):      K("Ctrl-Alt-Super-l"),
    # K("BACK"):                K("C-c"),
    K("KEY_SCREEN"):        K("c"),
    K("BTN_MISC"):          K("BACKSPACE"),
    K("ENTER"):             K("ENTER"),
    K("UP"):                K("UP"),
    K("DOWN"):              K("DOWN"),
    K("LEFT"):              K("LEFT"),
    K("RIGHT"):             K("RIGHT"),
    K("BTN_TL"):            K("g"),
    K("BTN_TL2"):           K("h"),
    K("BTN_THUMBL"):        K("KEY_102ND"),
    K("BTN_TR"):            K("MUTE"),
    K("BTN_TR2"):           K("PAGE_UP"),
    K("BTN_THUMBR"):        K("PAGE_DOWN"),
    K("HOMEPAGE"):          K("Ctrl-Shift-Alt-K"),
    K("KEY_SELECT"):        K("Super-f1"),
    # K("BTN_START"):         K("M-f1"),
}, "Global")

define_keymap(DEVICES['BDREMOTE'], lambda wm_class: wm_class in ["kodi", "vlc"], {
    K("KEY_AUDIO"):         K("a"),
    # K("KEY_ANGLE"):       K("Ctrl-Alt-Super-l"),
    K("KEY_SUBTITLE"):      K("l"),
    K("KEY_CLEAR"):         K("Shift-Ctrl-Alt-d"),
    # K("KEY_TIME"):            K("Ctrl-Alt-Super-l"),
    # K("KEY_RED"):             K("Ctrl-Alt-Super-l"),
    # K("KEY_GREEN"):       K("Ctrl-Alt-Super-l"),
    K("KEY_BLUE"):          [launch(["deluge-gtk &"]), sleep(1), launch(["deluge-gtk &"])],
    K("KEY_YELLOW"):        K("Super-e"),
    K("KEY_INFO"):          K("Super-p"),
    K("MENU"):              K("Alt-TAB"),
    # K("KEY_CONTEXT_MENU"):    K("Ctrl-Alt-Super-l"),
    K("ESC"):               K("Alt-f4"),
    # K("KEY_OPTION"):      K("Ctrl-Alt-Super-l"),
    K("BACK"):              K("C-c"),
    K("KEY_SCREEN"):        K("c"),
    K("BTN_MISC"):          K("BACKSPACE"),
    K("ENTER"):             K("ENTER"),
    K("UP"):                K("UP"),
    K("DOWN"):              K("DOWN"),
    K("LEFT"):              K("LEFT"),
    K("RIGHT"):             K("RIGHT"),
    K("BTN_TL"):            K("g"),
    K("BTN_TL2"):           K("h"),
    K("BTN_THUMBL"):        K("KEY_102ND"),
    K("BTN_TR"):            K("MUTE"),
    K("BTN_TR2"):           K("PAGE_UP"),
    K("BTN_THUMBR"):        K("PAGE_DOWN"),
    K("HOMEPAGE"):          K("esc"),
    K("KEY_SELECT"):        K("Super-f1"),
    # K("BTN_START"):         K("M-f1"),
    K("REWIND"):            K("r"),
    K("PLAY"):              K("SPACE"),
    K("FORWARD"):           K("f"),
    K("KEY_PREVIOUS"):      K("BACKSLASH"),
    K("STOP"):              K("x"),
    K("KEY_NEXT"):          K("RIGHT_BRACE"),
    K("KEY_FRAMEBACK"):     K("COMMA"),
    K("PAUSE"):             K("SPACE"),
    K("KEY_FRAMEFORWARD"):  K("DOT"),
}, "Kodi, vlc")

define_keymap(DEVICES['BDREMOTE'], lambda wm_class: wm_class in ['ksmserver', 'xfce4-session'], {
    K("EJECTCD"):           K("esc"),
    K("BTN_MISC"):          K("esc"),
    K("ENTER"):             K("ENTER"),
    K("LEFT"):              K("LEFT"),
    K("RIGHT"):             K("RIGHT"),
}, "ksmserver, xfce4-session")

define_keymap(DEVICES['BDREMOTE'], lambda wm_class: wm_class in ['firefox', 'brave-browser'], {
    K("KEY_AUDIO"):         K("a"),
    K("KEY_SUBTITLE"):      K("c"),
    K("KEY_CLEAR"):         K("Shift-C-M-d"),
    #
    K("KEY_YELLOW"):        K("Super-e"),
    K("KEY_INFO"):          K("Super-p"),
    K("MENU"):              K("M-TAB"),
    #
    K("ESC"):               K("M-f4"),
    #
    K("BACK"):              K("C-c"),
    K("KEY_SCREEN"):        K("c"),
    K("BTN_MISC"):          K("esc"),
    K("ENTER"):             K("ENTER"),
    K("UP"):                K("UP"),
    K("DOWN"):              K("DOWN"),
    K("LEFT"):              K("LEFT"),
    K("RIGHT"):             K("RIGHT"),
    #
    #
    K("BTN_THUMBL"):        K("f"),
    K("BTN_TR"):            K("m"),
    K("BTN_TR2"):           K("UP"),
    K("BTN_THUMBR"):        K("DOWN"),
    K("HOMEPAGE"):          K("esc"),
    #
    # K("BTN_START"):         K("M-f1"),
    K("REWIND"):            K("j"),
    #
    K("FORWARD"):           K("l"),
    K("KEY_PREVIOUS"):      K("BACKSLASH"),
    #
    K("KEY_NEXT"):          K("RIGHT_BRACE"),
    K("KEY_FRAMEBACK"):     K("RIGHT"),
    K("PAUSE"):             K("SPACE"),
    K("KEY_FRAMEFORWARD"):  K("LEFT"),
}, "Firefox, brave-browser")
