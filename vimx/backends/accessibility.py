import pyatspi
from gi.repository.GLib import GError


def get_children_of_interest(index, root, children):
    states = pyatspi.Atspi.StateSet()
    # attributes = {}
    x = -1
    y = -1
    width = 0
    length = 0

    try:
        states = root.get_state_set()
        # attributes = root.get_attributes()
        pos = root.get_position(pyatspi.DESKTOP_COORDS)

        x = pos.x
        y = pos.y
        size = root.get_size()
        width = size.x
        length = size.y
    except:
        pass

    if (
        x >= 0
        and y >= 0
        # and root.get_child_count() == 0
        # and attributes.get("hidden", "false") == "false"
        # and states.contains(
        #    pyatspi.state.STATE_SENSITIVE,
        # )
        and all(
            states.contains(state)
            for state in [
                pyatspi.state.STATE_SENSITIVE,
                pyatspi.state.STATE_ENABLED,
                pyatspi.state.STATE_VISIBLE,
                pyatspi.state.STATE_SHOWING,
            ]
        )
        # and any(
        #    states.contains(state)
        #    for state in [
        #        # pyatspi.state.STATE_ENABLED,
        #        pyatspi.state.STATE_VISIBLE,
        #        pyatspi.state.STATE_SHOWING,
        #    ]
        # )
    ):
        children.add((x + width / 2, y + length / 2))

    for child in root:
        get_children_of_interest(index + 1, child, children)

    return children


def active_window():
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        for window in app:
            if window.getState().contains(pyatspi.STATE_ACTIVE):
                return window


def get_children():
    children = set()
    get_children_of_interest(0, active_window(), children)
    return children
