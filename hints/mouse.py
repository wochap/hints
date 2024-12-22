"""Mouse handling functions."""

from __future__ import annotations

from enum import Enum
from time import time
from typing import TYPE_CHECKING, Any

from pynput import keyboard
from pynput.mouse import Button, Controller

from .utils import HintsConfig

if TYPE_CHECKING:
    from pynput.keyboard import KeyCode

KEY_PRESS_STATE: dict[str, Any] = {}


class MouseMode(Enum):
    """Mouse modes."""

    MOVE = 1
    SCROLL = 2


def on_release(key: KeyCode, mouse: Controller) -> bool | None:
    """Mouse release event handler.

    :param key: Key event.
    :param mouse: Mouse device.
    :return: keyhandler state
    """

    KEY_PRESS_STATE.clear()

    if key == keyboard.Key.esc:
        mouse.release(Button.left)
        return False

    return None


def do_mouse_action(
    key_press_state: dict[str, Any],
    config: HintsConfig,
    key: str,
    mouse: Controller,
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
    mouse_navigation_action = mouse.move
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

        mouse_navigation_action = mouse.move

    elif mode == MouseMode.SCROLL:
        sensitivity = config["mouse_scroll_pixel_sensitivity"]
        rampup_time = config["mouse_scroll_rampup_time"]
        left = config["mouse_scroll_left"]
        right = config["mouse_scroll_right"]
        up = config["mouse_scroll_up"]
        down = config["mouse_scroll_down"]
        mouse_navigation_action = mouse.scroll

    key_press_state.setdefault("sensitivity", sensitivity)

    if time() - key_press_state["start_time"] >= rampup_time:
        key_press_state["sensitivity"] += sensitivity

    if key == left:
        mouse_navigation_action(-key_press_state["sensitivity"], 0)
    if key == right:
        mouse_navigation_action(key_press_state["sensitivity"], 0)
    if key == up:
        mouse_navigation_action(0, key_press_state["sensitivity"])
    if key == down:
        mouse_navigation_action(0, -key_press_state["sensitivity"])


def on_press(key: KeyCode, config: HintsConfig, mouse: Controller, mode: MouseMode):
    """Mouse press event handler.

    :param key: Key event.
    :param config: Hints config.
    :param mouse: Mouse device.
    :param mode: Mouse mode (move/scroll).
    """
    try:
        do_mouse_action(KEY_PRESS_STATE, config, key.char, mouse, mode)
    except AttributeError:
        pass


def mouse_navigation(
    config: HintsConfig, mouse: Controller, mode: MouseMode = MouseMode.MOVE
):
    """Mouse navigation for mouse movement and scrolling.

    :param config: Config for hints.
    :param mouse: Mouse device.
    :param mode: Mode used for naviation (move / scroll).
    """
    with keyboard.Listener(
        on_press=lambda key: on_press(key, config, mouse, mode),
        on_release=lambda key: on_release(key, mouse),
    ) as listener:
        listener.join()
