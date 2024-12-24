"""Accessibility backend to get elements from an application using Atspi."""

import logging
from typing import Literal

from gi import require_version

require_version("Atspi", "2.0")
from gi.repository import Atspi

from hints.backends.backend import HintsBackend
from hints.backends.exceptions import AccessibleChildrenNotFoundError
from hints.child import Child

logger = logging.getLogger(__name__)


class AtspiBackend(HintsBackend):
    """Atspi backend class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = set()
        self.states_match_type = 0
        self.attributes = {}
        self.attributes_match_type = 0
        self.roles = set()
        self.roles_match_type = 0
        self.window_extents = (0, 0, 0, 0)

    def validate_match_conditions(
        self,
        root: Atspi.Accessible,
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
                if self.states_match_type in {
                    Atspi.CollectionMatchType.ALL,
                    Atspi.CollectionMatchType.EMPTY,
                }:
                    result = all(
                        state_set.contains(state_to_match)
                        for state_to_match in self.states
                    )
                elif self.states_match_type == Atspi.CollectionMatchType.ANY:
                    result = any(
                        state_set.contains(state_to_match)
                        for state_to_match in self.states
                    )
                elif self.states_match_type == Atspi.CollectionMatchType.NONE:
                    result = not any(
                        state_set.contains(state_to_match)
                        for state_to_match in self.states
                    )

            case "role":
                role = root.get_role()
                if self.roles_match_type in {
                    Atspi.CollectionMatchType.ALL,
                    Atspi.CollectionMatchType.EMPTY,
                }:
                    # for all elements to match means the only role must be
                    # in the set (like any)
                    # the other way to think about this is that roles is just
                    # one to check ie: role = {a_single_role}, but that does not
                    # seem very useful.
                    result = role in self.roles
                elif self.roles_match_type == Atspi.CollectionMatchType.ANY:
                    result = role in self.roles
                elif self.roles_match_type == Atspi.CollectionMatchType.NONE:
                    result = role not in self.roles
        return result

    def recursively_get_children_of_interest(
        self,
        root: Atspi.Accessible,
        children: set,
    ):
        """This is a fallback gathering method for when Applications do not
        implement the Collections interface.

        It is slower than using the Collection's interface, which is why
        it is a fallback method and not the primary way to gather
        accessible elements.

        :param root: Starting child.
        :param children: Set of coordinates for children to use to store
            found children coordinates.
        """
        try:
            if (
                self.validate_match_conditions(root, "state")
                and self.validate_match_conditions(root, "role")
                and self.window_extents
            ):
                logger.debug(
                    "Accessible element matched. Name: %s, ID: %d",
                    root.name,
                    root.get_id(),
                )
                logger.debug("role: %s", root.get_role())
                logger.debug("states: %s", root.get_state_set().get_states())

                relative_pos = root.get_position(Atspi.CoordType.WINDOW)
                size = root.get_size()
                children.add(
                    Child(
                        relative_position=(
                            relative_pos.x,
                            relative_pos.y,
                        ),
                        absolute_position=(
                            relative_pos.x + self.window_extents[0],
                            relative_pos.y + self.window_extents[1],
                        ),
                        width=size.x,
                        height=size.y,
                    )
                )
        except:
            pass

        for child_index in range(root.get_child_count()):
            self.recursively_get_children_of_interest(
                root.get_child_at_index(child_index),
                children,
            )

    def get_children_of_interest(
        self,
        root: Atspi.Accessible,
        children: set,
    ):
        """Get Atspi Accessible children that match a given set of states
        recursively.

        :param root: Starting child.
        :param children: Set of coordinates for children to use to store
            found children coordinates.
        """

        match_rule = Atspi.MatchRule.new(
            Atspi.StateSet.new(list(self.states)),
            self.states_match_type,
            self.attributes,
            self.attributes_match_type,
            list(self.roles),
            self.roles_match_type,
            [],
            Atspi.CollectionMatchType.ALL,
            False,
        )

        collection = root.get_collection_iface()

        if collection and self.window_extents:
            matches = collection.get_matches(
                match_rule, Atspi.CollectionSortOrder.CANONICAL, 0, True
            )

            for match in matches:
                logger.debug(
                    "Accessible element matched. Name: %s, ID: %d",
                    match.name,
                    match.get_id(),
                )
                logger.debug("role: %s", match.get_role())
                logger.debug("states: %s", match.get_state_set().get_states())

                relative_pos = match.get_position(Atspi.CoordType.WINDOW)
                size = match.get_size()
                children.add(
                    Child(
                        relative_position=(
                            relative_pos.x,
                            relative_pos.y,
                        ),
                        absolute_position=(
                            relative_pos.x + self.window_extents[0],
                            relative_pos.y + self.window_extents[1],
                        ),
                        width=size.x,
                        height=size.y,
                    )
                )
        else:
            logger.debug(
                "This application does not implement the collection interface,"
                " falling back to searching for Accessible elements recursively."
                " This could take a while depending on the number of elements in"
                " the application."
            )
            self.recursively_get_children_of_interest(
                root,
                children,
            )

    def active_window(self) -> Atspi.Accessible | None:
        """Get the current accessible window in focus.

        :return Focused window / accessible root element.
        """
        desktop = Atspi.get_desktop(0)
        for app_index in range(desktop.get_child_count()):
            window = desktop.get_child_at_index(app_index)
            for window_index in range(window.get_child_count()):
                current_window = window.get_child_at_index(window_index)
                if current_window.get_state_set().contains(Atspi.StateType.ACTIVE):
                    return current_window

        return None

    def get_children(
        self,
    ) -> set[Child]:
        """Get coordinates of children.

        :return: The extents of the window containing the children and
            centered children coordinates.
        """
        children: set[Child] = set()
        window = self.active_window()

        if window:
            application = window.get_application()
            toolkit = application.get_toolkit_name()
            version = application.get_toolkit_version()

            logger.debug("Gathering hints for '%s'", application.name)

            # GTK4 does not support desktop level positioning
            if toolkit == "GTK" and int(str(version).split(".", maxsplit=1)[0]) >= 4:
                logger.debug(
                    "This application is know not to support Atspi extents functionality,"
                    "falling back to getting information from the window manager."
                )
                self.window_extents = self.get_extents_from_window_manager()
            else:
                atspi_extents = window.get_extents(Atspi.CoordType.SCREEN)
                self.window_extents = (
                    atspi_extents.x,
                    atspi_extents.y,
                    atspi_extents.width,
                    atspi_extents.height,
                )

            all_match_rules = self.config["backends"]["atspi"]["match_rules"]
            match_rules = all_match_rules["default"] | all_match_rules.get(
                application.name, {}
            )

            self.states = set(match_rules["states"])
            self.states_match_type = match_rules["states_match_type"]
            self.attributes = match_rules["attributes"]
            self.attributes_match_type = match_rules["attributes_match_type"]
            self.roles = set(match_rules["roles"])
            self.roles_match_type = match_rules["roles_match_type"]

            self.get_children_of_interest(
                window,
                children,
            )

            if not children:
                raise AccessibleChildrenNotFoundError(window)

        return children
