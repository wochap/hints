from __future__ import annotations

import logging
from argparse import ArgumentParser
from itertools import product
from math import ceil, log
from time import time
from typing import Any, Iterable

from gi import require_version

from hints.backends.atspi import AtspiBackend
from hints.backends.exceptions import AccessibleChildrenNotFoundError
from hints.backends.opencv import OpenCV
from hints.exceptions import WindowSystemNotSupported
from hints.huds.interceptor import InterceptorWindow
from hints.huds.overlay import OverlayWindow
from hints.mouse import MouseButtonActions, MouseButtons, click
from hints.utils import HintsConfig, load_config
from hints.window_systems.window_system import WindowSystemType

# from pynput.mouse import Button, Controller


logger = logging.getLogger(__name__)


require_version("Gtk", "3.0")
from gi.repository import Gtk


def display_gkt_window(
    gtk_window: Gtk.Window,
    x: int,
    y: int,
    width: int,
    height: int,
    gkt_window_args: Iterable[Any] | None = None,
    gtk_window_kwargs: dict[str, Any] | None = None,
    overlay_x_offset: int = 0,
    overlay_y_offset: int = 0,
    is_wayland: bool = False,
):

    window = gtk_window(
        x + overlay_x_offset,
        y + overlay_y_offset,
        width,
        height,
        *(gkt_window_args or []),
        **gtk_window_kwargs,
    )

    if is_wayland:
        require_version("GtkLayerShell", "0.1")
        from gi.repository import GtkLayerShell

        GtkLayerShell.init_for_window(window)
        GtkLayerShell.set_margin(window, GtkLayerShell.Edge.LEFT, x + overlay_x_offset)
        GtkLayerShell.set_margin(window, GtkLayerShell.Edge.TOP, y + overlay_y_offset)
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_layer(window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.EXCLUSIVE)

    window.show_all()
    Gtk.main()


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


def hint_mode(config: HintsConfig, window_system: WindowSystem):
    """Hint mode to interact with hints on screen.

    :param config: Hints config.
    :param window_system: Window System for the session.
    """
    window_extents = None
    hints = {}

    backends_map = {"atspi": AtspiBackend, "opencv": OpenCV}
    backends = config["backends"]["enable"]

    is_wayland = window_system.window_system_type == WindowSystemType.WAYLAND

    for backend in backends:

        start = time()
        current_backend = backends_map[backend](config, window_system)
        logger.debug(
            "Attempting to get accessible children using the '%s' backend.",
            backend,
        )
        try:
            children = current_backend.get_children()

            logger.debug("Gathering hints took %f seconds", time() - start)
            logger.debug("Gathered %d hints", len(children))

            hints = get_hints(
                children,
                alphabet={
                    character
                    for character in config["alphabet"]
                    if not character.isdigit()
                },
            )

            window_extents = current_backend.window_system.focused_window_extents

        except AccessibleChildrenNotFoundError:
            logger.debug(
                "No acceessible children found with the '%s' backend.",
                backend,
            )

        if window_extents and hints:
            mouse_action: dict[str, Any] = {}
            x, y, width, height = window_extents

            display_gkt_window(
                OverlayWindow,
                x,
                y,
                width,
                height,
                gtk_window_kwargs={
                    "config": config,
                    "hints": hints,
                    "mouse_action": mouse_action,
                    "is_wayland": True,
                },
                overlay_x_offset=config["overlay_x_offset"],
                overlay_y_offset=config["overlay_y_offset"],
                is_wayland=True,
            )

            if mouse_action:

                mouse_x_offset = 0
                mouse_y_offset = 0

                match window_system.window_system_name:
                    case "sway":
                        mouse_y_offset = window_system.bar_height

                match mouse_action["action"]:
                    case "click":
                        click(
                            mouse_action["x"] + mouse_x_offset,
                            mouse_action["y"] + mouse_y_offset,
                            (
                                MouseButtons.LEFT
                                if mouse_action["button"] == "left"
                                else MouseButtons.RIGHT
                            ),
                            (MouseButtonActions.DOWN, MouseButtonActions.UP),
                            mouse_action["repeat"],
                        )
                    case "hover":
                        click(
                            mouse_action["x"] + mouse_x_offset,
                            mouse_action["y"] + mouse_y_offset,
                            MouseButtons.LEFT,
                            (),
                        )
                    case "grab":
                        click(
                            mouse_action["x"] + mouse_x_offset,
                            mouse_action["y"] + mouse_y_offset,
                            MouseButtons.LEFT,
                            (MouseButtonActions.DOWN,),
                        )

                        display_gkt_window(
                            InterceptorWindow,
                            x,
                            y,
                            1,
                            1,
                            gkt_window_args=({"action": "grab"},),
                            gtk_window_kwargs={"config": config},
                            is_wayland=is_wayland,
                        )

            # no need to use the next backend if the current one succeeded
            break


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

    window_system = None
    window_system_name = config["window_system"].lower()

    match window_system_name:
        case "x11":
            from hints.window_systems.x11 import X11 as window_system
        case "sway":
            from hints.window_systems.sway import Sway as window_system
        case _:
            raise WindowSystemNotSupported(window_system_name)

    ws = window_system()

    match args.mode:
        case "hint":
            hint_mode(config, ws)
        case "scroll":
            display_gkt_window(
                InterceptorWindow,
                0,
                0,
                1,
                1,
                gkt_window_args=({"action": "scroll"},),
                gtk_window_kwargs={"config": config},
                is_wayland=ws.window_system_type == WindowSystemType.WAYLAND,
            )
