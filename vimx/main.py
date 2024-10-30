#! /usr/bin/python

import gi
from backends.accessibility import get_children
from hud.overlay import Window
from itertools import product
from string import ascii_lowercase
from math import ceil, log
from subprocess import run

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell

    IS_WAYLAND = True
except ValueError:
    IS_WAYLAND = False

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def get_hints(children):
    hints = {}

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
    res_x = 3200
    res_y = 1800
    chidren = get_children()
    hints = get_hints(chidren)

    #print(len(chidren))

    if len(chidren) == 0:
        return

    click = {}
    app = Window(0, 0, res_x, res_y, hints=hints, click=click)
    # app = Window(0, 0, res_x, res_y, hints={"jk": (60, 10)}, click=click)

    # wayland
    if IS_WAYLAND:
        GtkLayerShell.init_for_window(app)
        GtkLayerShell.auto_exclusive_zone_enable(app)
        GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(app, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_layer(app, GtkLayerShell.Layer.OVERLAY)

    app.show_all()
    Gtk.main()

    # run(
    #    f"ydotool mousemove --absolute -x {click.get('x')} -y {click.get('y')}; ydotool click {click.get('button')}",
    #    check=False,
    #    shell=True,
    # )

    run(
        f"xdotool mousemove {click.get('x')} {click.get('y')}; xdotool click {'3' if click.get('button') =="right" else '1'}",
        check=False,
        shell=True,
    )


if __name__ == "__main__":
    main()
