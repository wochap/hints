from json import load
from typing import Any

import pyatspi

from .constants import CONFIG_PATH, DEFAULT_CONFIG

HintsConfig = dict[str, Any]


def parse_enums(config: HintsConfig) -> HintsConfig:
    """Parse enums in config to convert string values to Enums.

    This exits because the enum functionalities provided by GObject such as
    [get_value_by_name](https://docs.gtk.org/gobject/func.enum_get_value_by_name.html)
    requires that Enum classes are created. However the python GObject
    introspection does not support creating EnumClass Objects, which are needed
    to convert an Atspi g_type_class to an EnumClass to use such fucntionality.
    This is a work around, but is currently not being used as this was more of
    a thought experiment and parsing long configs with a lot of application
    configs could cause slow downs. This can be revisited if needed later to
    make writting configs easier. For now, configs can use constant values from
    the Atspi docs.

    :param config: Config to parse.
    """
    state_enums = {
        enum.value_name: enum
        for _, enum in pyatspi.Atspi.StateType.__enum_values__.items()
    }

    role_enums = {
        enum.value_name: enum for _, enum in pyatspi.Atspi.Role.__enum_values__.items()
    }

    atspi_application_rules = config["backends"]["atspi"]["match_rules"]

    for application, application_rules in atspi_application_rules.items():
        # states
        atspi_application_rules[application]["states"] = [
            state_enums[state] for state in application_rules.get("states", [])
        ]

        # roles
        atspi_application_rules[application]["roles"] = [
            role_enums[role] for role in application_rules.get("roles", [])
        ]

    return config


def merge_configs(source: HintsConfig, destination: HintsConfig) -> HintsConfig:
    """Deepmerge configs recursively.

    :param source: Source config.
    :param destination: Destination config.
    :return: Destination config.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_configs(value, node)
        else:
            destination[key] = value

    return destination


def load_config() -> HintsConfig:
    """Load Json config file.

    :return: config object.
    """
    config = {}

    try:
        with open(CONFIG_PATH, encoding="utf-8") as _f:
            config = load(_f)
    except FileNotFoundError:
        pass

    # return parse_enums(merge_configs(config, DEFAULT_CONFIG))
    return merge_configs(config, DEFAULT_CONFIG)
