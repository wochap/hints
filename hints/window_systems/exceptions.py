"""Window system exceptions."""

from typing import Iterable


class CouldNotIdentifyWindowSystemType(Exception):
    """Could not identify window sytem type exception."""

    def __str__(self):
        """String representation of exception."""
        return (
            "Could not identify Window System Type. Is the XDG_SESSION_TYPE"
            " environment variable set?"
        )


class WindowSystemNotSupported(Exception):
    """Window System not supported exception."""

    def __init__(self, supported_wms: Iterable[str]):
        """Exception constructor.

        :param window_system_name: The name of the window system that is
            not supported.
        """
        super().__init__()
        self.supported_wms = supported_wms

    def __str__(self) -> str:
        """String representation of exception."""
        return (
            "This window system is not supported, hints only supports one of: "
            f" {', '.join(self.supported_wms)}. To request support open an"
            " issue: https://github.com/AlfredoSequeida/hints/issues."
        )


class CouldNotFindWindowInformation(Exception):
    """Could not find window information."""

    def __init__(self, information_identifier: str):
        """Exception constructor.

        :param information_identified: A string identifier for the type
            of information that could not be found.
        """
        self.information_identifier = information_identifier

    def __str__(self) -> str:
        return f"Could not find {self.information_identifier} for the current window."


class CouldNotIdentifyActiveWindow(Exception):
    """Could not identify active window."""

    def __str__(self) -> str:
        return (
            "Could not find an active window. If you are using a"
            " Window Manager that is not EWMH compliant (such as DWM), you"
            " will be limited to applications that are supported by Atspi."
            " So you might not get hints on applications like terminals or"
            " applications that use GUI Frameworks without Atspi support."
        )
