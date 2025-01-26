"""Linux window manger."""

from gi import require_version

require_version("Atspi", "2.0")
require_version("Wnck", "3.0")

from enum import Enum

from gi.repository import Atspi, Wnck
from hints.window_systems.exceptions import (CouldNotFindWindowInformation,
                                             CouldNotIdentifyActiveWindow)
from hints.window_systems.window_system import WindowSystem


class WindowStrategy(Enum):
    WNCK = 0
    ATSPI = 1


class X11(WindowSystem):
    """Linux window manager class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.screen = Wnck.Screen.get_default()
        self.screen.force_update()
        self.active_window, self.window_strategy = self._get_active_window()

    def _get_active_window(
        self,
    ) -> tuple[Wnck.Window | Atspi.Accessible | None, WindowStrategy]:
        """Get active window.

        This method attempts to get the active window using libwnck.
        However, some window managers like DWM are not EWMH compliant
        and libwnck will not be able to get the active window. So as a
        fallback, we use Atspi.

        :return: The active window and the window strategy used to get
            the active window (WNCK or ATSPI).
        """

        active_window = self.screen.get_active_window()
        window_strategy = WindowStrategy.WNCK

        if not active_window:
            desktop = Atspi.get_desktop(0)
            for app_index in range(desktop.get_child_count()):
                window = desktop.get_child_at_index(app_index)
                # Gnome creates a mutter application that is also focused.
                # This is not what we want, so we are skipping it.
                if "mutter-x11-frames" in window.get_description():
                    continue
                for window_index in range(window.get_child_count()):
                    current_window = window.get_child_at_index(window_index)
                    if current_window.get_state_set().contains(Atspi.StateType.ACTIVE):
                        active_window = current_window
                        window_strategy = WindowStrategy.ATSPI
                        break
                if active_window:
                    break

        if not active_window:
            raise CouldNotIdentifyActiveWindow()

        return active_window, window_strategy

    @property
    def window_system_name(self) -> str:
        """Get the name of the window syste.

        This is useful for performing logic specific to a window system.

        :return: The window system name
        """
        return "x11"

    @property
    def focused_window_extents(self) -> tuple[int, int, int, int]:
        """Get active window extents.

        :return: Active window extents (x, y, width, height).
        """
        res = None

        match (self.window_strategy):
            case WindowStrategy.WNCK:
                res = self.active_window.get_geometry()
            case WindowStrategy.ATSPI:
                extents = self.active_window.get_extents(Atspi.CoordType.SCREEN)
                res = (extents.x, extents.y, extents.width, extents.height)

        if not res:
            raise CouldNotFindWindowInformation("window extents")

        return res

    @property
    def focused_window_pid(self) -> int:
        """Get Process ID corresponding to the focused widnow.

        :return: Process ID of focused window.
        """
        res = None

        match (self.window_strategy):
            case WindowStrategy.WNCK:
                res = self.active_window.get_pid()
            case WindowStrategy.ATSPI:
                res = self.active_window.get_process_id()

        if not res:
            raise CouldNotFindWindowInformation("process id")

        return res

    @property
    def focused_applicaiton_name(self) -> str:
        """Get focused application name.

        This name is the name used to identify applications for per-
        application rules.

        :return: Focused application name.
        """
        res = ""

        match (self.window_strategy):
            case WindowStrategy.WNCK:
                res = self.active_window.get_class_instance_name()
            case WindowStrategy.ATSPI:
                res = self.active_window.get_application().get_name()

        if not res:
            raise CouldNotFindWindowInformation("application name")

        return res
