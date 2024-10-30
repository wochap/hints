#! /usr/bin/python

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from test_window import TestWindow


def main():
    app = TestWindow()
    #app = Gtk.Window(title="test")
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
