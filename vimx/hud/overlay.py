#!/usr/bin/env python
from typing import Any

import cairo
from gi import require_foreign, require_version

require_version("Gtk", "3.0")
require_version("Gdk", "3.0")
require_foreign("cairo")

from gi.repository import Gdk, Gtk


class Window(Gtk.Window):
    """Composite widget to overlay hints over a window."""

    def __init__(
        self,
        width: float,
        height: float,
        hints: dict[str, tuple[int, int]],
        click: dict[str, Any],
    ):
        """Hint overlay constructor.
        :param width: Window width.
        :param height: Window height.
        :param hints: Hints to draw.
        :param click: Click to send.
        """
        super().__init__(1)

        self.width = width
        self.height = height
        self.hints = hints
        self.hint_selector_state = ""
        self.right_click = False
        self.click = click

        # composite setup
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.set_visual(visual)

        # window setup
        self.set_app_paintable(True)
        self.set_decorated(True)
        self.set_accept_focus(True)
        self.set_sensitive(True)
        self.set_default_size(self.width, self.height)

        self.da = Gtk.DrawingArea()

        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self.on_key_press)
        self.connect("show", self.on_grab)
        self.da.connect("draw", self.on_draw)

        def put_in_frame(widget):
            frame = Gtk.Frame(label=None)
            frame.set_property("shadow_type", Gtk.ShadowType.IN)
            frame.add(widget)
            return frame

        self.current_snippet = None

        vpaned = Gtk.VPaned()
        self.add(vpaned)
        vpaned.pack1(put_in_frame(self.da), True, True)

    def on_draw(self, _, cr):
        """Draw hints.
        :param cr: Cairo object.
        """
        hint_height = 40

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(20)

        for hint_value, pos in self.hints.items():
            x_loc, y_loc = pos
            if x_loc >= 0 and y_loc >= 0:
                cr.save()
                utf8 = hint_value

                x_bearing, y_bearing, width, height, _, _ = cr.text_extents(utf8)
                hint_width = width + 10

                cr.new_path()
                cr.translate(x_loc, y_loc)

                cr.rectangle(0, 0, hint_width, hint_height)
                cr.set_source_rgba(1, 81, 0.30, 0.6)
                cr.fill()

                cr.move_to(
                    (hint_width / 2) - (width / 2 + x_bearing),
                    (hint_height / 2) - (height / 2 + y_bearing),
                )
                cr.set_source_rgb(0, 0, 0)
                cr.show_text(utf8)
                cr.close_path()
                cr.restore()

    def on_key_press(self, _, event):
        """Handle key presses
        :param event: Event object.
        """
        keymap = Gdk.Keymap.get_default()

        state = Gdk.ModifierType(event.state & ~Gdk.ModifierType.LOCK_MASK)
        res = keymap.translate_keyboard_state(
            event.hardware_keycode,
            state,
            1,
        )

        keyval = res[1]
        consumed_modifiers = res[4]

        modifiers = (
            event.state & Gtk.accelerator_get_default_mod_mask() & ~consumed_modifiers
        )

        keyval_lower = Gdk.keyval_to_lower(keyval)

        if keyval_lower != keyval:
            modifiers |= Gdk.ModifierType.SHIFT_MASK
            self.right_click = True

        if keyval_lower == 65307:  # ESCAPE
            Gtk.main_quit()

        # select hint
        next_hint_char = chr(keyval_lower)

        # only update selector state if next char makes up a possible valid hint
        if self.hint_selector_state + next_hint_char in {
            choice[: len(self.hint_selector_state) + 1] for choice in self.hints
        }:
            self.hint_selector_state += next_hint_char
            if self.hint_selector_state in self.hints:
                Gdk.keyboard_ungrab(event.time)
                self.destroy()
                x, y = self.hints.get(self.hint_selector_state)
                self.click["x"] = x
                self.click["y"] = y
                # self.click["button"] = "0xC1" if self.right_click else "0xC0"
                self.click["button"] = "right" if self.right_click else "left"

    def on_grab(self, window):
        """Force keyboard grab to listen for keybaord events.
        :param window: Window object.
        """
        while (
            Gdk.keyboard_grab(window.get_window(), False, Gdk.CURRENT_TIME)
            != Gdk.GrabStatus.SUCCESS
        ):
            pass


# Useful for testing hints on the fly by calling module
if __name__ == "__main__":
    res_x = 2560
    res_y = 1440
    app = HintWindow(
        0,
        0,
        res_x,
        res_y,
        hints={(10, 10), (300, 10)},
    )
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
