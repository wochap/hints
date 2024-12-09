from __future__ import annotations

from itertools import product
from json import load
from math import ceil, log
from os import path
from string import ascii_lowercase
from subprocess import run
from typing import TYPE_CHECKING, Any, Iterable

from gi import require_version

from .backends.accessibility import get_children
from .hud.overlay import Window

if TYPE_CHECKING:
    from .child import Child

try:
    require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell

    IS_WAYLAND = True
except ValueError:
    IS_WAYLAND = False

require_version("Gtk", "3.0")
from gi.repository import Gtk


def get_hints(children: set, alphabet: Iterable = ascii_lowercase) -> dict[str, Child]:
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


def load_config() -> dict[str, Any]:
    """Load Json config file :return: config object."""
    config = {}

    with open(
        path.join(path.expanduser("~"), ".config/hints/config.json"), encoding="utf-8"
    ) as _f:
        config = load(_f)

    return config


def main():
    """Hints entry point."""

    config = load_config()

    window_extents, chidren = get_children()
    hints = get_hints(
        chidren,
        alphabet={
            character
            for character in config.get("alphabet", ascii_lowercase)
            if not character.isdigit()
        },
    )

    if window_extents and hints:
        click = {}
        app = Window(
            window_extents.x,
            window_extents.y,
            window_extents.width,
            window_extents.height,
            hints=hints,
            click=click,
            **config["hints"],
        )

        if IS_WAYLAND:
            GtkLayerShell.init_for_window(app)
            GtkLayerShell.auto_exclusive_zone_enable(app)
            GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_layer(app, GtkLayerShell.Layer.OVERLAY)

        app.show_all()
        Gtk.main()

        if click:
            for _ in range(click["repeat"]):
                run(
                    f"xdotool mousemove {click.get('x')} {click.get('y')}; xdotool click {'3' if click.get('button') =="right" else '1'}",
                    check=False,
                    shell=True,
                )
