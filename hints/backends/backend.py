from __future__ import annotations

from typing import TYPE_CHECKING

from hints.utils import HintsConfig
from hints.window_manager import WindowManager

if TYPE_CHECKING:
    from hints.child import Child
    from hints.window_manager import Wnck


class HintsBackend:
    """Hints Backend Base Class."""

    def __init__(self, config: HintsConfig):
        self.config = config
        self.window_extents: tuple[int, int, int, int] | None = None
        self.window_manager = WindowManager()

    def get_children(self) -> set[Child]:
        """Get Children from backend."""
        raise NotImplementedError()

    def get_active_window(self) -> Wnck.Window:
        """Get active window from window manager.

        :return: Active window.
        """
        return self.window_manager.get_active_window()

    def get_extents_from_window_manager(self) -> tuple[int, int, int, int]:
        """Get extents for active window from window manager.

        :return: extents (x,y,width,height).
        """
        return self.get_active_window().get_geometry()

    def get_window_extents(self) -> tuple[int, int, int, int]:
        """Get window extents from class if available or from window manager if
        not available.

        :return: (x_position, y_position, width, height)
        """
        return self.window_extents or self.get_extents_from_window_manager()
