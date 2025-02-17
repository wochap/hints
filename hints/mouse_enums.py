"""Common mouse enums."""

from enum import Enum

from evdev import ecodes


class MouseButton(Enum):
    """Mouse Buttons."""

    LEFT = ecodes.BTN_LEFT
    RIGHT = ecodes.BTN_RIGHT


class MouseButtonState(Enum):
    """Mouse Button States."""

    DOWN = 1
    UP = 0


class MouseMode(Enum):
    """Mouse modes."""

    MOVE = 1
    SCROLL = 2
