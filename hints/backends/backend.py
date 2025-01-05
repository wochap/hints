from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hints.utils import HintsConfig

if TYPE_CHECKING:
    from hints.child import Child
    from hints.window_systems.window_system import WindowSystem


class HintsBackend:
    """Hints Backend Base Class."""

    def __init__(self, config: HintsConfig, window_system: WindowSystem):
        """Hints Backend constructor.

        :param config: Hints config.
        """
        self.backend_name = ""
        self.config = config
        self.window_system = window_system

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
            self.window_system.focused_applicaiton_name, {}
        )

    def get_children(self) -> list[Child]:
        """Get Children from backend."""
        raise NotImplementedError()
