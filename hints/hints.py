from __future__ import annotations

import logging
from argparse import ArgumentParser
from enum import Enum
from itertools import product
from math import ceil, log
from time import sleep, time
from typing import TYPE_CHECKING, Any

from gi import require_version
from pynput import keyboard
from pynput.mouse import Button, Controller

from .backends.accessibility import get_children
from .constants import MOUSE_GRAB_PAUSE
from .hud.overlay import Window
from .utils import HintsConfig, load_config

if TYPE_CHECKING:
    from pynput.keyboard import KeyCode

    from .child import Child

try:
    require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell

    IS_WAYLAND = True
except ValueError:
    IS_WAYLAND = False

require_version("Gtk", "3.0")
from gi.repository import Gtk

KEY_PRESS_STATE: dict[str, Any] = {"sensitivity": 10}


class MouseMode(Enum):
    MOVE = 1
    SCROLL = 2


def get_hints(children: set, alphabet: str | set[str]) -> dict[str, Child]:
    """Get hints.

    :param children: The children elements of windown that indicate the
        absolute position of those elements.
    :param alphabet: The alphabet used to create hints
    :return: The hints. Ex {"ab": Child, "ac": Child}
    """
    hints: dict[str, Child] = {}

    if len(children) == 0:
        return hints

    for child, hint in zip(
        children,
        product(alphabet, repeat=ceil(log(len(children)) / log(len(alphabet)))),
    ):
        hints["".join(hint)] = child

    return hints


def hint_mode(config: HintsConfig, mouse: Controller):
    """Hint mode to interact with hints on screen.

    :param config: Hints config.
    :param mouse: Mouse device.
    """
    window_extents, chidren = get_children(config)
    hints = get_hints(
        chidren,
        alphabet={
            character for character in config["alphabet"] if not character.isdigit()
        },
    )

    if window_extents and hints:
        mouse_action: dict[str, Any] = {}
        x, y, width, height = window_extents
        app = Window(
            x,
            y,
            width,
            height,
            hints=hints,
            mouse_action=mouse_action,
            **config["hints"],
            exit_key=config["exit_key"],
            hover_modifier=["hover_modifier"],
            grab_modifier=config["grab_modifier"],
        )

        if IS_WAYLAND:
            GtkLayerShell.init_for_window(app)
            GtkLayerShell.auto_exclusive_zone_enable(app)
            GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_layer(app, GtkLayerShell.Layer.OVERLAY)

        app.show_all()
        Gtk.main()

        if mouse_action:
            match mouse_action["action"]:
                case "click":
                    mouse.position = (mouse_action["x"], mouse_action["y"])
                    mouse.click(
                        (
                            Button.left
                            if mouse_action["button"] == "left"
                            else Button.right
                        ),
                        mouse_action["repeat"],
                    )
                case "hover":
                    mouse.position = (mouse_action["x"], mouse_action["y"])
                case "grab":
                    mouse.position = (mouse_action["x"], mouse_action["y"])
                    # sleep required to allow time for mouse to move before pressing
                    # less than 0.2 seconds does not always work
                    sleep(MOUSE_GRAB_PAUSE)
                    mouse.press(Button.left)
                    mouse_navigation(config, mouse)


def on_press(key: KeyCode, config: HintsConfig, mouse: Controller, mode: MouseMode):
    """Mouse press event handler.

    :param key: Key event.
    :param config: Hints config.
    :param mouse: Mouse device.
    :param mode: Mouse mode (move/scroll).
    """
    try:
        KEY_PRESS_STATE.setdefault("start_time", time())

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
            right = config["MOUSE_SCROLL_RIGHT"]
            up = config["mouse_scroll_up"]
            down = config["mouse_scroll_down"]
            mouse_navigation_action = mouse.scroll

        KEY_PRESS_STATE.setdefault("sensitivity", sensitivity)

        if time() - KEY_PRESS_STATE["start_time"] >= rampup_time:
            KEY_PRESS_STATE["sensitivity"] += sensitivity

        if key.char == left:
            mouse_navigation_action(-KEY_PRESS_STATE["sensitivity"], 0)
        if key.char == right:
            mouse_navigation_action(KEY_PRESS_STATE["sensitivity"], 0)
        if key.char == up:
            mouse_navigation_action(0, KEY_PRESS_STATE["sensitivity"])
        if key.char == down:
            mouse_navigation_action(0, -KEY_PRESS_STATE["sensitivity"])

    except AttributeError:
        pass


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


def main():
    """Hints entry point."""

    config = load_config()

    parser = ArgumentParser(
        prog="Hints",
        description="Hints lets you navigate GUI applications in Linux without"
        ' your mouse by displaying "hints" you can type on your keyboard to'
        " interact with GUI elements.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="hint",
        choices=["hint", "scroll"],
        help="mode to use",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Set verbosity of output. Useful for debugging and seeing the"
        " output of accessible elements (roles, states, application name, ect)"
        " for setting up configuration.",
    )

    args = parser.parse_args()

    custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if args.verbose >= 1:
        logging.basicConfig(level=logging.DEBUG, format=custom_format)
    else:
        logging.basicConfig(level=logging.INFO, format=custom_format)

    mouse = Controller()

    match args.mode:
        case "hint":
            hint_mode(config, mouse)
        case "scroll":
            mouse_navigation(config, mouse, MouseMode.SCROLL)
