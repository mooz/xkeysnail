from enum import Enum, unique, IntEnum

__author__ = 'zh'


class Key(IntEnum):
    RESERVED = 0
    ESC = 1
    KEY_1 = 2
    KEY_2 = 3
    KEY_3 = 4
    KEY_4 = 5
    KEY_5 = 6
    KEY_6 = 7
    KEY_7 = 8
    KEY_8 = 9
    KEY_9 = 10
    KEY_0 = 11
    MINUS = 12
    EQUAL = 13
    BACKSPACE = 14
    TAB = 15
    Q = 16
    W = 17
    E = 18
    R = 19
    T = 20
    Y = 21
    U = 22
    I = 23
    O = 24
    P = 25
    LEFT_BRACE = 26
    RIGHT_BRACE = 27
    ENTER = 28
    LEFT_CTRL = 29
    A = 30
    S = 31
    D = 32
    F = 33
    G = 34
    H = 35
    J = 36
    K = 37
    L = 38
    SEMICOLON = 39
    APOSTROPHE = 40
    GRAVE = 41
    LEFT_SHIFT = 42
    BACKSLASH = 43
    Z = 44
    X = 45
    C = 46
    V = 47
    B = 48
    N = 49
    M = 50
    COMMA = 51
    DOT = 52
    SLASH = 53
    RIGHT_SHIFT = 54
    KPASTERISK = 55
    LEFT_ALT = 56
    SPACE = 57
    CAPSLOCK = 58
    F1 = 59
    F2 = 60
    F3 = 61
    F4 = 62
    F5 = 63
    F6 = 64
    F7 = 65
    F8 = 66
    F9 = 67
    F10 = 68
    NUMLOCK = 69
    SCROLLLOCK = 70
    KP7 = 71
    KP8 = 72
    KP9 = 73
    KPMINUS = 74
    KP4 = 75
    KP5 = 76
    KP6 = 77
    KPPLUS = 78
    KP1 = 79
    KP2 = 80
    KP3 = 81
    KP0 = 82
    KPDOT = 83

    ZENKAKUHANKAKU = 85
    KEY_102ND = 86
    F11 = 87
    F12 = 88
    RO = 89
    KATAKANA = 90
    HIRAGANA = 91
    HENKAN = 92
    KATAKANAHIRAGANA = 93
    MUHENKAN = 94
    KPJPCOMMA = 95
    KPENTER = 96
    RIGHT_CTRL = 97
    KPSLASH = 98
    SYSRQ = 99
    RIGHT_ALT = 100
    LINEFEED = 101
    HOME = 102
    UP = 103
    PAGE_UP = 104
    LEFT = 105
    RIGHT = 106
    END = 107
    DOWN = 108
    PAGE_DOWN = 109
    INSERT = 110
    DELETE = 111
    MACRO = 112
    MUTE = 113
    VOLUMEDOWN = 114
    VOLUMEUP = 115
    POWER = 116
    KPEQUAL = 117
    KPPLUSMINUS = 118
    PAUSE = 119
    SCALE = 120

    KPCOMMA = 121
    HANGEUL = 122
    HANGUEL = HANGEUL
    HANJA = 123
    YEN = 124
    LEFT_META = 125
    RIGHT_META = 126
    COMPOSE = 127

    STOP = 128
    AGAIN = 129
    PROPS = 130
    UNDO = 131
    FRONT = 132
    COPY = 133
    OPEN = 134
    PASTE = 135
    FIND = 136
    CUT = 137
    HELP = 138
    MENU = 139
    CALC = 140
    SETUP = 141
    SLEEP = 142
    WAKEUP = 143
    FILE = 144
    SENDFILE = 145
    DELETEFILE = 146
    XFER = 147
    PROG1 = 148
    PROG2 = 149
    WWW = 150
    MSDOS = 151
    COFFEE = 152
    SCREENLOCK = COFFEE
    DIRECTION = 153
    CYCLEWINDOWS = 154
    MAIL = 155
    BOOKMARKS = 156
    COMPUTER = 157
    BACK = 158
    FORWARD = 159
    CLOSECD = 160
    EJECTCD = 161
    EJECTCLOSECD = 162
    NEXTSONG = 163
    PLAYPAUSE = 164
    PREVIOUSSONG = 165
    STOPCD = 166
    RECORD = 167
    REWIND = 168
    PHONE = 169
    ISO = 170
    CONFIG = 171
    HOMEPAGE = 172
    REFRESH = 173
    EXIT = 174
    MOVE = 175
    EDIT = 176
    SCROLLUP = 177
    SCROLLDOWN = 178
    KPLEFTPAREN = 179
    KPRIGHTPAREN = 180
    NEW = 181
    REDO = 182

    F13 = 183
    F14 = 184
    F15 = 185
    F16 = 186
    F17 = 187
    F18 = 188
    F19 = 189
    F20 = 190
    F21 = 191
    F22 = 192
    F23 = 193
    F24 = 194

    PLAYCD = 200
    PAUSECD = 201
    PROG3 = 202
    PROG4 = 203
    DASHBOARD = 204
    SUSPEND = 205
    CLOSE = 206
    PLAY = 207
    FASTFORWARD = 208
    BASSBOOST = 209
    PRINT = 210
    HP = 211
    CAMERA = 212
    SOUND = 213
    QUESTION = 214
    EMAIL = 215
    CHAT = 216
    SEARCH = 217
    CONNECT = 218
    FINANCE = 219
    SPORT = 220
    SHOP = 221
    ALTERASE = 222
    CANCEL = 223
    BRIGHTNESSDOWN = 224
    BRIGHTNESSUP = 225
    MEDIA = 226

    SWITCHVIDEOMODE = 227
    KBDILLUMTOGGLE = 228
    KBDILLUMDOWN = 229
    KBDILLUMUP = 230

    SEND = 231
    REPLY = 232
    FORWARDMAIL = 233
    SAVE = 234
    DOCUMENTS = 235

    BATTERY = 236

    BLUETOOTH = 237
    WLAN = 238
    UWB = 239

    UNKNOWN = 240

    VIDEO_NEXT = 241
    VIDEO_PREV = 242
    BRIGHTNESS_CYCLE = 243
    BRIGHTNESS_AUTO = 244
    BRIGHTNESS_ZERO = BRIGHTNESS_AUTO
    DISPLAY_OFF = 245

    WWAN = 246
    WIMAX = WWAN
    RFKILL = 247

    MICMUTE = 248


@unique
class Action(IntEnum):

    RELEASE, PRESS, REPEAT = range(3)

    def is_pressed(self):
        return self == Action.PRESS or self == Action.REPEAT


@unique
class Modifier(Enum):

    CONTROL, ALT, SHIFT = range(3)

    @classmethod
    def _get_modifier_map(cls):
        return {
            cls.CONTROL: {Key.LEFT_CTRL, Key.RIGHT_CTRL},
            cls.ALT: {Key.LEFT_ALT, Key.RIGHT_ALT},
            cls.SHIFT: {Key.LEFT_SHIFT, Key.RIGHT_SHIFT}
        }

    def get_keys(self):
        return self._get_modifier_map()[self]

    def get_key(self):
        return next(iter(self.get_keys()))

    @classmethod
    def get_all_keys(cls):
        return {key for keys in cls._get_modifier_map().values() for key in keys}

    @staticmethod
    def from_key(key):
        for modifier in Modifier:
            if key in modifier.get_keys():
                return modifier


class Combo:

    def __init__(self, modifiers, key):

        if isinstance(modifiers, list):
            raise ValueError("modifiers should be a set instead of a list")
        elif modifiers is None:
            modifiers = set()
        elif isinstance(modifiers, Modifier):
            modifiers = {modifiers}
        elif not isinstance(modifiers, set):
            raise ValueError("modifiers should be a set")

        if not isinstance(key, Key):
            raise ValueError("key should be a Key")

        self.modifiers = modifiers
        self.key = key

    def __eq__(self, other):
        if isinstance(other, Combo):
            return self.modifiers == other.modifiers and self.key == other.key
        else:
            return NotImplemented

    def __hash__(self):
        return hash((frozenset(self.modifiers), self.key))

    def __str__(self):
        return "{}, {}".format(str(self.modifiers), str(self.key))

    def with_modifier(self, modifiers):
        if isinstance(modifiers, Modifier):
            modifiers = {modifiers}
        return Combo(self.modifiers | modifiers, self.key)
