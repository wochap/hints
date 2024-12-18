"""Overlay to display hints over an application window."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import cairo
from gi import require_foreign, require_version

from ..constants import DEFAULT_CONFIG

require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
require_foreign("cairo")

from gi.repository import Gdk, Gtk

if TYPE_CHECKING:
    from ..child import Child


class Window(Gtk.Window):
    """Composite widget to overlay hints over a window."""

    def __init__(
        self,
        x_pos: int,
        y_pos: int,
        width: int,
        height: int,
        hints: dict[str, Child],
        mouse_action: dict[str, Any],
        hint_height=40,
        hint_width_padding=10,
        hint_font_size=20,
        hint_font_face="Sans",
        hint_font_r=0,
        hint_font_g=0,
        hint_font_b=0,
        hint_font_a=1,
        hint_upercase=True,
        hint_background_r=1,
        hint_background_g=81,
        hint_background_b=0.30,
        hint_background_a=0.6,
        exit_key=DEFAULT_CONFIG["exit_key"],
        hover_modifier=DEFAULT_CONFIG["hover_modifier"],
        grab_modifier=DEFAULT_CONFIG["grab_modifier"],
    ):
        """Hint overlay constructor.

        :param width: Window width.
        :param height: Window height.
        :param hints: Hints to draw.
        :param mouse_action: Mouse action to send.
        """
        super().__init__(Gtk.WindowType.POPUP)

        self.width = width
        self.height = height
        self.hints = hints
        self.hint_selector_state = ""
        self.mouse_action = mouse_action

        # hint settings
        self.hint_height = hint_height
        self.hint_width_padding = hint_width_padding

        self.hint_font_size = hint_font_size
        self.hint_font_face = hint_font_face
        self.hint_font_r = hint_font_r
        self.hint_font_g = hint_font_g
        self.hint_font_b = hint_font_b
        self.hint_font_a = hint_font_a
        self.hint_upercase = hint_upercase

        self.hint_background_r = hint_background_r
        self.hint_background_g = hint_background_g
        self.hint_background_b = hint_background_b
        self.hint_background_a = hint_background_a

        self.exit_key = exit_key
        self.grab_modifier = grab_modifier
        self.hover_modifier = hover_modifier

        # composite setup
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.set_visual(visual)

        # window setup
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_accept_focus(True)
        self.set_sensitive(True)
        self.set_default_size(self.width, self.height)
        self.move(x_pos, y_pos)

        self.drawing_area = Gtk.DrawingArea()

        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self.on_key_press)
        self.connect("show", self.on_grab)
        self.drawing_area.connect("draw", self.on_draw)

        def put_in_frame(widget):
            frame = Gtk.Frame(label=None)
            frame.set_property("shadow_type", Gtk.ShadowType.IN)
            frame.add(widget)
            return frame

        self.current_snippet = None

        vpaned = Gtk.VPaned()
        self.add(vpaned)
        vpaned.pack1(put_in_frame(self.drawing_area), True, True)

    def on_draw(self, _, cr):
        """Draw hints.

        :param cr: Cairo object.
        """
        hint_height = self.hint_height

        cr.select_font_face(
            self.hint_font_face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        cr.set_font_size(self.hint_font_size)

        for hint_value, child in self.hints.items():
            x_loc, y_loc = child.relative_position
            if x_loc >= 0 and y_loc >= 0:
                cr.save()
                utf8 = hint_value.upper() if self.hint_upercase else hint_value

                x_bearing, y_bearing, width, height, _, _ = cr.text_extents(utf8)
                hint_width = width + self.hint_width_padding

                cr.new_path()
                cr.translate(x_loc, y_loc)

                cr.rectangle(0, 0, hint_width, hint_height)
                cr.set_source_rgba(
                    self.hint_background_r,
                    self.hint_background_g,
                    self.hint_background_b,
                    self.hint_background_a,
                )
                cr.fill()

                cr.move_to(
                    (hint_width / 2) - (width / 2 + x_bearing),
                    (hint_height / 2) - (height / 2 + y_bearing),
                )

                cr.set_source_rgba(
                    self.hint_font_r,
                    self.hint_font_g,
                    self.hint_font_b,
                    self.hint_font_a,
                )
                cr.show_text(utf8)
                cr.close_path()
                cr.restore()

    def update_hints(self, next_char: str):
        """Update hints on screen to eliminate options.

        :param next_char: Next character for hint_selector_state.
        """

        updated_hints = {
            hint: child
            for hint, child in self.hints.items()
            if hint.startswith(self.hint_selector_state + next_char)
        }

        if updated_hints:
            self.hints = updated_hints
            self.hint_selector_state += next_char

        self.drawing_area.queue_draw()

    def on_key_press(self, _, event):
        """Handle key presses :param event: Event object."""
        keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())

        # if keyval is bound, keyval, effective_group, level, consumed_modifiers
        _, keyval, _, _, consumed_modifiers = keymap.translate_keyboard_state(
            event.hardware_keycode,
            Gdk.ModifierType(event.state & ~Gdk.ModifierType.LOCK_MASK),
            1,
        )

        modifiers = (
            # current state, default mod mask, consumed modifiers
            event.state
            & Gtk.accelerator_get_default_mod_mask()
            & ~consumed_modifiers
        )

        keyval_lower = Gdk.keyval_to_lower(keyval)

        if keyval_lower == self.exit_key:
            Gtk.main_quit()

        if modifiers == self.hover_modifier:
            self.mouse_action.update({"action": "hover"})

        if modifiers == self.grab_modifier:
            self.mouse_action.update({"action": "grab"})

        if keyval_lower != keyval:
            self.mouse_action.update({"action": "click", "button": "right"})

        hint_chr = chr(keyval_lower)

        if hint_chr.isdigit():
            self.mouse_action.update(
                {"repeat": int(f"{self.mouse_action.get('repeat', '')}{hint_chr}")}
            )

        self.update_hints(hint_chr)

        if len(self.hints) == 1:
            Gdk.keyboard_ungrab(event.time)
            self.destroy()
            x, y = self.hints[self.hint_selector_state].absolute_position
            self.mouse_action.update(
                {
                    "action": self.mouse_action.get("action", "click"),
                    "x": x,
                    "y": y,
                    "repeat": self.mouse_action.get("repeat", 1),
                    "button": self.mouse_action.get("button", "left"),
                }
            )

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
