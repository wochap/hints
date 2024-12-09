"""Accessibility backend to get elements from an application using Atspi."""

import pyatspi

from ..child import Child
from .exceptions import (AccessibleChildrenNotFoundError,
                         CouldNotFindAccessibleWindow)


def get_children_of_interest(
    index: int,
    root: pyatspi.Atspi.Accessible,
    state_conditions: list[int],
    children: set,
) -> set[Child]:
    """Get Atspi Accessible children that match a given set of states
    recursively.

    :param index: Starting child index for root.
    :param root: Starting child.
    :param state_condtions: The conditions to match children against.
    :param children: Set of coordinates for children to use to store
        found children coordinates.
    :return: All matched centered children coordinates.
    """

    states = pyatspi.Atspi.StateSet()
    relative_x = -1
    relative_y = -1
    absolute_x = -1
    absolute_y = -1
    width = 0
    length = 0

    try:
        states = root.get_state_set()
        relative_pos = root.get_position(pyatspi.WINDOW_COORDS)
        absolute_pos = root.get_position(pyatspi.DESKTOP_COORDS)

        relative_x = relative_pos.x
        relative_y = relative_pos.y
        absolute_x = absolute_pos.x
        absolute_y = absolute_pos.y
        size = root.get_size()
        width = size.x
        length = size.y
    except:
        pass

    if (
        relative_x >= 0
        and relative_y >= 0
        and all(states.contains(state) for state in state_conditions)
    ):
        children.add(
            Child(
                relative_position=(relative_x + width / 2, relative_y + length / 2),
                absolute_position=(
                    absolute_x + width / 2,
                    absolute_y + length / 2,
                ),
            )
        )

    for child in root:
        get_children_of_interest(index + 1, child, state_conditions, children)

    return children


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
        [
            pyatspi.STATE_SENSITIVE,
            pyatspi.STATE_ENABLED,
            pyatspi.STATE_VISIBLE,
            pyatspi.STATE_SHOWING,
        ],
        children,
    )

    if not children:
        raise AccessibleChildrenNotFoundError(active_window)

    return window.get_extents(pyatspi.DESKTOP_COORDS), children
