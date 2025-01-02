"""Linux window system."""

from enum import Enum
from os import getenv


class CouldNotIdentifyWindowSystemType(Exception):
    def __str__(self):
        return (
            "Could not identify Window System Type. Is the XDG_SESSION_TYPE"
            " environment variable set?"
        )


class WindowSystemType(Enum):
    X11 = "x11"
    WAYLAND = "wayland"


class WindowSystem:
    """Linux base window system class."""

    def __init__(self):
        self.xdg_session_type = getenv("XDG_SESSION_TYPE")

        if not self.xdg_session_type:
            raise CouldNotIdentifyWindowSystemType()

    @property
    def window_system_type(self) -> WindowSystemType:
        """Get window_sysetm_type.

        :return: The window system type.
        """
        return WindowSystemType(self.xdg_session_type)

    @property
    def window_system_name(self) -> str:
        """Get the name of the window syste.

        This is useful for performing logic specific to a window system.

        :return: The window system name
        """
        raise NotImplementedError()

    @property
    def focused_window_extents(self) -> tuple[int, int, int, int]:
        """Get active window extents.

        :return: Active window extents (x, y, width, height).
        """
        raise NotImplementedError()

    @property
    def focused_window_pid(self) -> int:
        """Get Process ID corresponding to the focused widnow.

        :return: Process ID of focused window.
        """
        raise NotImplementedError()

    @property
    def focused_applicaiton_name(self) -> str:
        """Get focused application name.

        This name is the name used to identify applications for per-
        application rules.

        :return: Focused application name.
        """
        raise NotImplementedError()
