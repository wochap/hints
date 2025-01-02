"""Mouse handling functions."""

from __future__ import annotations

from enum import Enum
from subprocess import run
from time import time
from typing import TYPE_CHECKING, Any, Iterable

from hints.utils import HintsConfig

# from pynput import keyboard
# from pynput.mouse import Button, Controller


if TYPE_CHECKING:
    from pynput.keyboard import KeyCode

KEY_PRESS_STATE: dict[str, Any] = {}


class MouseMode(Enum):
    """Mouse modes."""

    MOVE = 1
    SCROLL = 2


class MouseButtons(Enum):
    LEFT = 0x00
    RIGHT = 0x01
    MIDDLE = 0x02
    SIDE = 0x03
    EXTR = 0x04
    FORWARD = 0x05
    BACK = 0x06
    TASK = 0x07


class MouseButtonActions(Enum):
    DOWN = 0x40
    UP = 0x80


def scroll(x: int | str, y: int | str, *_args, **_wargs):
    run(["ydotool", "mousemove", "--wheel", "--", str(x), str(y)], check=True)


def move(x: int | str, y: int | str, absolute: bool = True):
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


# def on_release(key: KeyCode, mouse: Controller) -> bool | None:
#    """Mouse release event handler.
#
#    :param key: Key event.
#    :param mouse: Mouse device.
#    :return: keyhandler state
#    """
#
#    KEY_PRESS_STATE.clear()
#
#    if key == keyboard.Key.esc:
#        mouse.release(Button.left)
#        return False
#
#    return None

# def on_press(key: KeyCode, config: HintsConfig, mouse: Controller, mode: MouseMode):
#    """Mouse press event handler.
#
#    :param key: Key event.
#    :param config: Hints config.
#    :param mouse: Mouse device.
#    :param mode: Mouse mode (move/scroll).
#    """
#    try:
#        do_mouse_action(KEY_PRESS_STATE, config, key.char, mouse, mode)
#    except AttributeError:
#        pass


# def mouse_navigation(
#    config: HintsConfig, mouse: Controller, mode: MouseMode = MouseMode.MOVE
# ):
#    """Mouse navigation for mouse movement and scrolling.
#
#    :param config: Config for hints.
#    :param mouse: Mouse device.
#    :param mode: Mode used for naviation (move / scroll).
#    """
#    with keyboard.Listener(
#        on_press=lambda key: on_press(key, config, mouse, mode),
#        on_release=lambda key: on_release(key, mouse),
#    ) as listener:
#        listener.join()
