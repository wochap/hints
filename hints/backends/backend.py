from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hints.utils import HintsConfig
from hints.window_manager import WindowManager

if TYPE_CHECKING:
    from hints.child import Child
    from hints.window_manager import Wnck


class HintsBackend:
    """Hints Backend Base Class."""

    def __init__(self, config: HintsConfig):
        """Hints Backend constructor.

        :param config: Hints config.
        """
        self.config = config

        self.window_manager = WindowManager()
        self.backend_name = ""
        self.active_window = self.get_active_window()
        self.window_extents = self.active_window.get_geometry()
        self.application_name = self.active_window.get_class_instance_name()

    def get_application_rules(self) -> dict[str, Any]:
        """Get the application rules from the config file.

        This uses the "default" application rule and overwrites any
        rules specific to an application by the application name.

        :return: The application rules
        """
        application_rules = self.config["backends"][self.backend_name][
            "application_rules"
        ]
        return application_rules["default"] | application_rules.get(
            self.application_name, {}
        )

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
