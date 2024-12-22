"""Accessibility backend to get elements from an application using Atspi."""

import logging
from time import time
from typing import Literal

import pyatspi

from ..child import Child
from ..platform_utils.linux.window_manager import WindowManager
from ..utils import HintsConfig
from .exceptions import (AccessibleChildrenNotFoundError,
                         CouldNotFindAccessibleWindow)

logger = logging.getLogger(__name__)


def validate_match_conditions(
    root: pyatspi.Atspi.Accessible,
    match_against: set[pyatspi.Atspi.StateType | pyatspi.Atspi.Role],
    condition: pyatspi.Atspi.CollectionMatchType,
    match_type: Literal["state", "role"],
) -> bool:
    """Validate matching conditions for atspi match types.

    :param root: Accessible element to validate.
    :param match_against: Set to match against.
    :param conditions: Condition to match for.
    :param match_type: The type of matching to do.
    """
    result = False
    match match_type:
        case "state":
            state_set = root.get_state_set()
            match condition:
                case pyatspi.Collection.MATCH_ALL:
                    result = all(
                        state_set.contains(state_to_match)
                        for state_to_match in match_against
                    )
                case pyatspi.Collection.MATCH_ANY:
                    result = any(
                        state_set.contains(state_to_match)
                        for state_to_match in match_against
                    )
                case pyatspi.Collection.MATCH_NONE:
                    result = not any(
                        state_set.contains(state_to_match)
                        for state_to_match in match_against
                    )

        case "role":
            role = root.get_role()
            match condition:
                case pyatspi.Collection.MATCH_ALL:
                    # for all elements to match means the only role must be
                    # in the set (like any)
                    # the other way to think about this is that roles is just
                    # one to check ie: role = {a_single_role}, but that does not
                    # seem very useful.
                    result = role in match_against
                case pyatspi.Collection.MATCH_ANY:
                    result = role in match_against
                case pyatspi.Collection.MATCH_NONE:
                    result = not role in match_against
    return result


def recursively_get_children_of_interest(
    root: pyatspi.Atspi.Accessible,
    children: set,
    states: set[pyatspi.Atspi.StateType],
    states_match_type: pyatspi.Atspi.CollectionMatchType,
    attributes: dict[str, str],
    attributes_match_type: pyatspi.Atspi.CollectionMatchType,
    roles: set[pyatspi.Atspi.Role],
    roles_match_type: pyatspi.Atspi.CollectionMatchType,
    absolute_x_offeset: int,
    absolute_y_offeset: int,
):
    """This is a fallback gathering method for when Applications do not
    implement the Collections interface.

    It is slower than using the Collection's interface, which is why it
    is a fallback method and not the primary way to gather accessible
    elements.

    :param root: Starting child.
    :param children: Set of coordinates for children to use to store
        found children coordinates.
    :param states: States to match against.
    :param states_match_type: Match type enum.
    :param attributes: Attributes to match against.
    :param attributes_match_type: Match type enum.
    :param roles: Roles to match against.
    :param roles_match_type: Match type enum.
    :param abosolute_x_offset: Absolute offset x based on Window
        position.
    :param abosolute_y_offset: Absolute offset y based on Window
        position.
    """
    try:
        if validate_match_conditions(
            root, states, states_match_type, "state"
        ) and validate_match_conditions(root, roles, roles_match_type, "role"):

            logger.debug(
                "Accessible element matched name: %s, id: %d, text: %s",
                root.name,
                root.id,
                root.get_text(),
            )
            logger.debug("role: %s", root.get_role())
            logger.debug("states: %s", root.get_state_set().get_states())

            relative_pos = root.get_position(pyatspi.WINDOW_COORDS)
            if relative_pos.x >= 0 and relative_pos.y >= 0:
                children.add(
                    Child(
                        relative_position=(
                            relative_pos.x,
                            relative_pos.y,
                        ),
                        absolute_position=(
                            relative_pos.x + absolute_x_offeset,
                            relative_pos.y + absolute_y_offeset,
                        ),
                    )
                )
    except:
        pass

    for child in root:
        recursively_get_children_of_interest(
            child,
            children,
            states,
            states_match_type,
            attributes,
            attributes_match_type,
            roles,
            roles_match_type,
            absolute_x_offeset,
            absolute_y_offeset,
        )


def get_children_of_interest(
    root: pyatspi.Atspi.Accessible,
    children: set,
    states: list[pyatspi.Atspi.StateType],
    states_match_type: pyatspi.Atspi.CollectionMatchType,
    attributes: dict[str, str],
    attributes_match_type: pyatspi.Atspi.CollectionMatchType,
    roles: list[pyatspi.Atspi.Role],
    roles_match_type: pyatspi.Atspi.CollectionMatchType,
    absolute_x_offeset: int,
    absolute_y_offeset: int,
):
    """Get Atspi Accessible children that match a given set of states
    recursively.

    :param root: Starting child.
    :param children: Set of coordinates for children to use to store
        found children coordinates.
    :param states: States to match against.
    :param states_match_type: Match type enum.
    :param attributes: Attributes to match against.
    :param attributes_match_type: Match type enum.
    :param roles: Roles to match against.
    :param roles_match_type: Match type enum.
    :param abosolute_x_offset: Absolute offset x based on Window
        position.
    :param abosolute_y_offset: Absolute offset y based on Window
        position.
    """

    match_rule = pyatspi.Atspi.MatchRule.new(
        pyatspi.StateSet(*states),
        states_match_type,
        attributes,
        attributes_match_type,
        roles,
        roles_match_type,
        [],
        pyatspi.Collection.MATCH_ALL,
        False,
    )

    collection = root.get_collection_iface()

    if collection:
        matches = collection.get_matches(
            match_rule, pyatspi.Collection.SORT_ORDER_CANONICAL, 0, True
        )

        for match in matches:
            logger.debug(
                "Accessible element matched name: %s, id: %d, text: %s",
                match.name,
                match.id,
                match.get_text(),
            )
            logger.debug("role: %s", match.get_role())
            logger.debug("states: %s", match.get_state_set().get_states())

            relative_pos = match.get_position(pyatspi.WINDOW_COORDS)
            children.add(
                Child(
                    relative_position=(
                        relative_pos.x,
                        relative_pos.y,
                    ),
                    absolute_position=(
                        relative_pos.x + absolute_x_offeset,
                        relative_pos.y + absolute_y_offeset,
                    ),
                )
            )
    else:
        logger.debug(
            "This application does not implement the collection interface,"
            " falling back to searching for Accessible elements recursively."
            " This could take a while depending on the number of elements in"
            " the application."
        )
        recursively_get_children_of_interest(
            root,
            children,
            set(states),
            states_match_type,
            attributes,
            attributes_match_type,
            set(roles),
            roles_match_type,
            absolute_x_offeset,
            absolute_y_offeset,
        )


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


def get_extents_from_window_manager() -> tuple[int, int, int, int]:
    """Get extents for active window from window manager.

    :return: extents (x,y,width,height).
    """
    return WindowManager().get_active_window().get_geometry()


def get_children(
    config: HintsConfig,
) -> tuple[tuple[int, int, int, int] | None, set[Child]]:
    """Get coordinates of children.

    :return: The extents of the window containing the children and
        centered children coordinates.
    """
    children: set[Child] = set()
    window = active_window()
    application = window.get_application()
    toolkit = application.get_toolkit_name()
    version = application.get_toolkit_version()

    logger.debug("Gathering hints for '%s'", application.name)

    window_extents: tuple[int, int, int, int] = (0, 0, 0, 0)

    # GTK4 does not support desktop level positioning
    if toolkit == "GTK" and int(str(version).split(".", maxsplit=1)[0]) >= 4:
        logger.debug(
            "This application is know not to support Atspi extents functionality,"
            "falling back to getting information from the window manager."
        )
        window_extents = get_extents_from_window_manager()
    else:
        atspi_extents = window.get_extents(pyatspi.DESKTOP_COORDS)
        window_extents = (
            atspi_extents.x,
            atspi_extents.y,
            atspi_extents.width,
            atspi_extents.height,
        )

    if window_extents:

        all_match_rules = config["backends"]["atspi"]["match_rules"]
        match_rules = all_match_rules["default"] | all_match_rules.get(
            application.name, {}
        )

        start = time()

        get_children_of_interest(
            window,
            children,
            match_rules["states"],
            match_rules["states_match_type"],
            match_rules["attributes"],
            match_rules["attributes_match_type"],
            match_rules["roles"],
            match_rules["roles_match_type"],
            window_extents[0],
            window_extents[1],
        )

        logger.debug("Gathering hints took %f seconds", time() - start)
        logger.debug("Gathered %d hints", len(children))

        if not children:
            raise AccessibleChildrenNotFoundError(active_window)

    return window_extents, children
