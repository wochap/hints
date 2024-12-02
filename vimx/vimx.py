#! /usr/bin/python

from itertools import product
from math import ceil, log
from string import ascii_lowercase
from subprocess import run
from sys import platform

from gi import require_version

from .backends.accessibility import get_children
from .hud.overlay import Window

try:
    require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell

    IS_WAYLAND = True
except ValueError:
    IS_WAYLAND = False

require_version("Gtk", "3.0")
from gi.repository import Gtk


def get_hints(children: set) -> dict[str, tuple[int, int]]:
    """Get hints.

    :param children: The children elements of windown that indicate the
        absolute position of those elements.
    :return: The hints. Ex {"ab": (0,0), "ac": (10,100)}
    """
    hints: dict[str, tuple[int, int]] = {}

    if len(children) == 0:
        return hints

    for child, hint in zip(
        children,
        product(
            ascii_lowercase, repeat=ceil(log(len(children)) / log(len(ascii_lowercase)))
        ),
    ):
        hints["".join(hint)] = child

    return hints


def main():
    """vimx entry point."""

    system = None

    if "linux" in platform:
        from vimx.platform_utils import linux as system
    elif "win32" in platform:
        raise NotImplementedError("Windows not supported yet.")
    elif "darwin" in platform:
        raise NotImplementedError("OSX not supported yet.")

    if system:
        w, h = system.get_screen_resolution()
        chidren = get_children()
        hints = get_hints(chidren)

        click = {}
        app = Window(w, h, hints=hints, click=click)

        # wayland
        if IS_WAYLAND:
            GtkLayerShell.init_for_window(app)
            GtkLayerShell.auto_exclusive_zone_enable(app)
            GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_layer(app, GtkLayerShell.Layer.OVERLAY)

        app.show_all()
        Gtk.main()

        run(
            f"xdotool mousemove {click.get('x')} {click.get('y')}; xdotool click {'3' if click.get('button') =="right" else '1'}",
            check=False,
            shell=True,
        )
