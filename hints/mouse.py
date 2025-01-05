"""Mouse handling functions."""

from __future__ import annotations

from enum import Enum
from subprocess import run
from time import time
from typing import Any, Iterable

from hints.utils import HintsConfig

KEY_PRESS_STATE: dict[str, Any] = {}


class MouseMode(Enum):
    """Mouse modes."""

    MOVE = 1
    SCROLL = 2


class MouseButtons(Enum):
    """Ydotool Mouse buttons bit mask codes."""

    LEFT = 0x00
    RIGHT = 0x01
    MIDDLE = 0x02
    SIDE = 0x03
    EXTR = 0x04
    FORWARD = 0x05
    BACK = 0x06
    TASK = 0x07


class MouseButtonActions(Enum):
    """Ydotool Mouse actions bit mask codes."""

    DOWN = 0x40
    UP = 0x80


def scroll(x: int | str, y: int | str, *_args, **_kwargs):
    """Scroll Mouse using ydotool.

    :param x: X scroll direction.
    :param y: Y scroll direction. :param *_args: Extra args to use the
        same interface as move. :param **_kwargs: Extra kwargs to use
        the same interface as move.
    """
    run(["ydotool", "mousemove", "--wheel", "--", str(x), str(y)], check=True)


def move(x: int | str, y: int | str, absolute: bool = True):
    """Move mouse using ydotool.

    :param X: X move direction.
    :param y: Y move direction.
    :param absolute: Whether to move the mouse using an absolute
        position.
    """
    move_cmd = ["ydotool", "mousemove"]
    move_cmd += ["--absolute"] if absolute else []
    run(move_cmd + ["--", str(x), str(y)], check=True)


def do_mouse_action(
    key_press_state: dict[str, Any],
    config: HintsConfig,
    key: str,
    mode: MouseMode,
):
    """Perform mouse action.

    :param key_press_state: State containing key press event data used
        for ramping up speeds.
    :param config: Hints config.
    :param key: The key to perform a mouse action for.
    :param mode: The mouse mode.
    """
    key_press_state.setdefault("start_time", time())

    sensitivity = 1
    rampup_time = 1
    mouse_navigation_action = move
    left = "h"
    right = "l"
    up = "k"
    down = "j"

    if mode == MouseMode.MOVE:
        sensitivity = config["mouse_move_pixel_sensitivity"]
        rampup_time = config["mouse_move_rampup_time"]
        left = config["mouse_move_left"]
        right = config["mouse_move_right"]

        # up and down are intentionally switched to keep the logic the same
        # as scrol
        up = config["mouse_move_down"]
        down = config["mouse_move_up"]

        mouse_navigation_action = move

    elif mode == MouseMode.SCROLL:
        sensitivity = config["mouse_scroll_pixel_sensitivity"]
        rampup_time = config["mouse_scroll_rampup_time"]
        left = config["mouse_scroll_left"]
        right = config["mouse_scroll_right"]
        up = config["mouse_scroll_up"]
        down = config["mouse_scroll_down"]
        mouse_navigation_action = scroll

    key_press_state.setdefault("sensitivity", sensitivity)

    if time() - key_press_state["start_time"] >= rampup_time:
        key_press_state["sensitivity"] += sensitivity

    if key == left:
        mouse_navigation_action(-key_press_state["sensitivity"], 0, absolute=False)
    if key == right:
        mouse_navigation_action(key_press_state["sensitivity"], 0, absolute=False)
    if key == up:
        mouse_navigation_action(0, key_press_state["sensitivity"], absolute=False)
    if key == down:
        mouse_navigation_action(0, -key_press_state["sensitivity"], absolute=False)


def click(
    x: int | str,
    y: int | str,
    button: MouseButtons,
    actions: Iterable[MouseButtonActions],
    repeat: int | str = 1,
    absolute: bool = True,
):
    """Click using ydotool.

    :param x: X position to click.
    :param y: Y position to click.
    :param button: Button to use for click.
    :param actions: Actions to use for the click button.
    :param repeat: Times to repeat a click.
    :param absolute: Whether the click position is absolute.
    """
    move(x, y, absolute=absolute)

    button_mask = button.value
    for action in actions:
        button_mask |= action.value

    run(
        [
            "ydotool",
            "click",
            str(hex(button_mask)),
            "--repeat",
            str(repeat),
        ],
        check=True,
    )
