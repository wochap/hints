"""Mouse service for hints.

This service is an independent application that hints calls using a Unix
Domain Socket to perform mouse movements by writing to uinput. We use
custom uinput devices to support X11 and Wayland. This is separate from
the main hints application to prevent slowing down the main hints
process when creating virutal devices.
"""

from __future__ import annotations

from multiprocessing.connection import Listener
from os import path, remove
from time import sleep, time
from typing import TYPE_CHECKING, Any, Iterable

from evdev import AbsInfo, UInput, ecodes
from gi import require_version

from hints.constants import SOCK_FILE
from hints.mouse_enums import MouseButton, MouseMode
from hints.utils import load_config

require_version("Gdk", "3.0")
from gi.repository import Gdk

KEY_PRESS_STATE: dict[str, Any] = {}

if TYPE_CHECKING:
    from hints.mouse_enums import MouseButtonState


config = load_config()


class Mouse:
    """Mouse class for performing mouse actions (click, hover, move, etc).

    This uses uinput to support both X11 and Wayland.
    """

    def __init__(self, abs_max_width=10000, abs_max_height=10000, write_pause=0.03):

        keys = [button.value for button in MouseButton]
        self.write_pause = write_pause

        self.relative_mouse = UInput(
            {
                ecodes.EV_KEY: keys,
                ecodes.EV_REL: [
                    ecodes.REL_X,
                    ecodes.REL_Y,
                    ecodes.REL_HWHEEL,
                    ecodes.REL_WHEEL,
                ],
            },
            name="Hints relative mouse",
        )

        self.absolute_mouse = UInput(
            {
                ecodes.EV_KEY: keys,
                ecodes.EV_ABS: [
                    (
                        ecodes.ABS_X,
                        AbsInfo(
                            value=0,
                            min=0,
                            max=abs_max_width,
                            fuzz=0,
                            flat=0,
                            resolution=0,
                        ),
                    ),
                    (
                        ecodes.ABS_Y,
                        AbsInfo(
                            value=0,
                            min=0,
                            max=abs_max_height,
                            fuzz=0,
                            flat=0,
                            resolution=0,
                        ),
                    ),
                ],
            },
            name="Hints absolute mouse",
        )

    def scroll(self, x: int, y: int, *_args, **_kwargs):
        """Scroll event.

        :param x: X scroll direction.
        :param y: Y scroll direction. :param *_args: Extra args to use
            the same interface as move. :param **_kwargs: Extra kwargs
            to use the same interface as move.
        """
        self.relative_mouse.write(ecodes.EV_REL, ecodes.REL_HWHEEL, int(x))
        self.relative_mouse.write(ecodes.EV_REL, ecodes.REL_WHEEL, int(y))
        self.relative_mouse.syn()

    def move(self, x: int, y: int, absolute: bool = True):
        """Move event.

        :param X: X move direction.
        :param y: Y move direction.
        :param absolute: Whether to move the mouse using an absolute
            position.
        """

        if absolute:
            self.absolute_mouse.write(ecodes.EV_ABS, ecodes.ABS_X, int(x))
            self.absolute_mouse.write(ecodes.EV_ABS, ecodes.ABS_Y, int(y))
            self.absolute_mouse.syn()

        else:
            self.relative_mouse.write(ecodes.EV_REL, ecodes.REL_X, int(x))
            self.relative_mouse.write(ecodes.EV_REL, ecodes.REL_Y, int(y))
            self.relative_mouse.syn()

        sleep(self.write_pause)

    def click(
        self,
        x: int,
        y: int,
        button: MouseButton,
        button_states: Iterable[MouseButtonState],
        repeat: int = 1,
        absolute: bool = True,
    ):
        """Click event.

        :param x: X position to click.
        :param y: Y position to click.
        :param button: Button to use for click.
        :param actions: Actions to use for the click button (button down
            / button up).
        :param repeat: Times to repeat a click.
        :param absolute: Whether the click position is absolute.
        """
        self.move(x, y, absolute=absolute)

        for _ in range(repeat):
            for button_state in button_states:
                self.relative_mouse.write(ecodes.EV_KEY, button, button_state)
                self.relative_mouse.syn()
                sleep(self.write_pause)

        # small move to clear previous write incase the previous move wants to be
        # repeated
        self.move(x + 1, y, absolute=True)
        self.move(x - 1, y, absolute=True)

    def do_mouse_action(
        self,
        key_press_state: dict[str, Any],
        key: str,
        mode: MouseMode,
    ):
        """Perform mouse action.

        :param key_press_state: State containing key press event data
            used for ramping up speeds.
        :param key: The key to perform a mouse action for.
        :param mode: The mouse mode.
        """
        key_press_state.setdefault("start_time", time())

        sensitivity = 1
        rampup_time = 1
        mouse_navigation_action = self.move
        left = "h"
        right = "l"
        up = "k"
        down = "j"

        if mode == MouseMode.MOVE.value:
            sensitivity = config["mouse_move_pixel_sensitivity"]
            rampup_time = config["mouse_move_rampup_time"]
            left = config["mouse_move_left"]
            right = config["mouse_move_right"]

            # up and down are intentionally switched to keep the logic the same
            # as scrol
            up = config["mouse_move_down"]
            down = config["mouse_move_up"]

            mouse_navigation_action = self.move

        elif mode == MouseMode.SCROLL.value:
            sensitivity = config["mouse_scroll_pixel_sensitivity"]
            rampup_time = config["mouse_scroll_rampup_time"]
            left = config["mouse_scroll_left"]
            right = config["mouse_scroll_right"]
            up = config["mouse_scroll_up"]
            down = config["mouse_scroll_down"]
            mouse_navigation_action = self.scroll

        key_press_state.setdefault("sensitivity", sensitivity)

        if time() - key_press_state["start_time"] >= rampup_time:
            key_press_state["sensitivity"] += sensitivity

        if key == left:
            mouse_navigation_action(-key_press_state["sensitivity"], 0, absolute=False)
        if key == right:
            mouse_navigation_action(key_press_state["sensitivity"], 0, absolute=False)
        if key == up:
            mouse_navigation_action(0, key_press_state["sensitivity"], absolute=False)
        if key == down:
            mouse_navigation_action(0, -key_press_state["sensitivity"], absolute=False)


def main():
    """Mouse service entry point."""
    screen = Gdk.Display.get_default().get_default_screen()
    mouse = Mouse(screen.get_width(), screen.get_height())

    if path.exists(SOCK_FILE):
        remove(SOCK_FILE)

    with Listener(SOCK_FILE) as listener:
        while True:
            with listener.accept() as conn:

                payload = conn.recv()
                method = payload.get("method", "")
                args = payload.get("args", ())
                kwargs = payload.get("kwargs", {})

                match (method):
                    case "click":
                        mouse.click(*args, **kwargs)
                    case "move":
                        mouse.move(*args, **kwargs)
                    case "scroll":
                        mouse.scroll(*args, **kwargs)
                    case "do_mouse_action":
                        mouse.do_mouse_action(*args, **kwargs)


if __name__ == "__main__":
    main()
