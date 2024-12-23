"""Global constant values."""

from os import path

import pyatspi
from gi import require_version

require_version("Gdk", "3.0")
from gi.repository import Gdk

CONFIG_PATH = path.join(path.expanduser("~"), ".config/hints/config.json")
MOUSE_GRAB_PAUSE = 0.2
DEFAULT_CONFIG = {
    "hints": {
        "hint_height": 30,
        "hint_width_padding": 10,
        "hint_font_size": 15,
        "hint_font_face": "Sans",
        "hint_font_r": 0,
        "hint_font_g": 0,
        "hint_font_b": 0,
        "hint_font_a": 1,
        "hint_pressed_font_r": 0.7,
        "hint_pressed_font_g": 0.7,
        "hint_pressed_font_b": 0.4,
        "hint_pressed_font_a": 1,
        "hint_upercase": True,
        "hint_background_r": 1,
        "hint_background_g": 1,
        "hint_background_b": 0.5,
        "hint_background_a": 0.8,
    },
    "backends": {
        "atspi": {
            "match_rules": {
                "default": {
                    "states": [
                        pyatspi.STATE_SENSITIVE,
                        pyatspi.STATE_SHOWING,
                        pyatspi.STATE_VISIBLE,
                    ],
                    "states_match_type": pyatspi.Collection.MATCH_ALL,
                    "attributes": {},
                    "attributes_match_type": pyatspi.Collection.MATCH_ALL,
                    "roles": [
                        # containers
                        pyatspi.ROLE_PANEL,
                        pyatspi.ROLE_SECTION,
                        pyatspi.ROLE_HTML_CONTAINER,
                        pyatspi.ROLE_FRAME,
                        pyatspi.ROLE_MENU_BAR,
                        pyatspi.ROLE_TOOL_BAR,
                        pyatspi.ROLE_LIST,
                        pyatspi.ROLE_PAGE_TAB_LIST,
                        pyatspi.ROLE_DESCRIPTION_LIST,
                        pyatspi.ROLE_SCROLL_PANE,
                        pyatspi.ROLE_TABLE,
                        # text
                        pyatspi.ROLE_STATIC,
                        pyatspi.ROLE_HEADING,
                        pyatspi.ROLE_PARAGRAPH,
                        pyatspi.ROLE_DESCRIPTION_VALUE,
                        # other
                        pyatspi.ROLE_LANDMARK,
                        pyatspi.ROLE_FILLER,
                        pyatspi.ROLE_DESCRIPTION_TERM,
                    ],
                    "roles_match_type": pyatspi.Collection.MATCH_NONE,
                },
            },
        }
    },
    "alphabet": "asdfgqwertzxcvbhjklyuiopnm",
    "mouse_move_left": "h",
    "mouse_move_right": "l",
    "mouse_move_up": "k",
    "mouse_move_down": "j",
    "mouse_scroll_left": "h",
    "mouse_scroll_right": "l",
    "mouse_scroll_up": "k",
    "mouse_scroll_down": "j",
    "mouse_move_pixel": 10,
    "mouse_move_pixel_sensitivity": 10,
    "mouse_move_rampup_time": 0.5,
    "mouse_scroll_pixel": 5,
    "mouse_scroll_pixel_sensitivity": 5,
    "mouse_scroll_rampup_time": 0.5,
    "exit_key": Gdk.KEY_Escape,
    "hover_modifier": Gdk.ModifierType.CONTROL_MASK,
    "grab_modifier": Gdk.ModifierType.MOD1_MASK,  # Alt
}
