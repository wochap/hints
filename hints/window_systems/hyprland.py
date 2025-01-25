"""Sway window system."""

from json import loads
from subprocess import run

from hints.window_systems.window_system import WindowSystem


class Hyprland(WindowSystem):
    """Sway Window system class."""

    def __init__(self):
        super().__init__()
        self.focused_window = self._get_focused_window_from_hyprlandctl()

    def _get_focused_window_from_hyprlandctl(self):
        focused_window = run(
            ["hyprctl", "activewindow", "-j"], capture_output=True, check=True
        )
        return loads(focused_window.stdout.decode("utf-8"))

    @property
    def window_system_name(self) -> str:
        """Get the name of the window syste.

        This is useful for performing logic specific to a window system.

        :return: The window system name
        """
        return "Hyprland"

    @property
    def focused_window_extents(self) -> tuple[int, int, int, int]:
        """Get active window extents.

        :return: Active window extents (x, y, width, height).
        """
        x, y = self.focused_window["at"]
        width, height = self.focused_window["size"]
        return (x, y, width, height)

    @property
    def focused_window_pid(self) -> int:
        """Get Process ID corresponding to the focused widnow.

        :return: Process ID of focused window.
        """
        return self.focused_window["pid"]

    @property
    def focused_applicaiton_name(self) -> str:
        """Get focused application name.

        This name is the name used to identify applications for per-
        application rules.

        :return: Focused application name.
        """
        return self.focused_window["class"]
