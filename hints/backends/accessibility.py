"""Accessibility backend to get elements from an application using Atspi."""

import pyatspi

from ..child import Child
from .exceptions import (AccessibleChildrenNotFoundError,
                         CouldNotFindAccessibleWindow)

EXPECTED_STATE_CONDITIONS = [
    pyatspi.STATE_SENSITIVE,
    pyatspi.STATE_ENABLED,
    pyatspi.STATE_VISIBLE,
    pyatspi.STATE_SHOWING,
]


def get_children_of_interest(
    index: int,
    root: pyatspi.Atspi.Accessible,
    children: set,
):
    """Get Atspi Accessible children that match a given set of states
    recursively.

    :param index: Starting child index for root.
    :param root: Starting child.
    :param children: Set of coordinates for children to use to store
        found children coordinates.
    """
    try:
        if all(
            root.get_state_set().contains(state) for state in EXPECTED_STATE_CONDITIONS
        ):
            relative_pos = root.get_position(pyatspi.WINDOW_COORDS)
            if relative_pos.x >= 0 and relative_pos.y >= 0:
                absolute_pos = root.get_position(pyatspi.DESKTOP_COORDS)
                size = root.get_size()
                children.add(
                    Child(
                        relative_position=(
                            relative_pos.x + size.x / 2,
                            relative_pos.y + size.y / 2,
                        ),
                        absolute_position=(
                            absolute_pos.x + size.x / 2,
                            absolute_pos.y + size.y / 2,
                        ),
                    )
                )
    except:
        pass

    for child in root:
        get_children_of_interest(index + 1, child, children)


def active_window() -> pyatspi.Atspi.Accessible:
    """Get the current accessible window in focus.

    :return Focused window / accessible root element.
    """

    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        for window in app:
            if window.getState().contains(pyatspi.STATE_ACTIVE):
                return window

    raise CouldNotFindAccessibleWindow()


def get_children() -> tuple[pyatspi.Atspi.Rect, set[Child]]:
    """Get coordinates of children.

    :return: The extents of the window containing the children and
        centered children coordinates.
    """
    children: set[Child] = set()
    window = active_window()

    get_children_of_interest(
        0,
        window,
        children,
    )

    if not children:
        raise AccessibleChildrenNotFoundError(active_window)

    return window.get_extents(pyatspi.DESKTOP_COORDS), children
