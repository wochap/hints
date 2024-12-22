"""Linux window manger."""

from gi import require_version

require_version("Wnck", "3.0")

from gi.repository import Wnck


class WindowManager:
    """Linux window manager class."""

    def __init__(self):
        self.screen = Wnck.Screen.get_default()

    def get_active_window(self) -> Wnck.Window:
        """Get active window.

        :return: active window.
        """
        self.screen.force_update()
        return self.screen.get_active_window()

    def get_window_extents(self, pid: int) -> tuple[int, int, int, int] | None:
        """Get Window extents by window pid.

        :param pid: Process id.
        :return: Window extents if found.
        """
        self.screen.force_update()
        for window in self.screen.get_windows():
            if window.get_pid() == pid:
                return window.get_geometry()

        return None
