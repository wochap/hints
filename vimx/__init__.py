"""Vimx."""

from json import dump
from os import environ, makedirs, path

__version__ = "0.0.1"
__config__ = {
    "hints": {
        "hint_height": 30,
        "hint_width_padding": 10,
        "hint_font_size": 15,
        "hint_font_face": "Sans",
        "hint_font_background_r": 1,
        "hint_font_background_g": 1,
        "hint_font_background_b": 0.5,
        "hint_font_background_a": 0.6,
    }
}


dir_path_to_conf = path.join(path.expanduser("~"), ".config/vimx")

if "XDG_CONFIG_HOME" in environ:
    dir_path_to_conf = environ["XDG_CONFIG_HOME"]

# setting up config file with setting options
file_path_to_conf = path.join(dir_path_to_conf, "config.json")

if not path.exists(dir_path_to_conf):
    makedirs(dir_path_to_conf)

if not path.exists(file_path_to_conf):
    with open(file_path_to_conf, "w+", encoding="utf-8") as _f:
        dump(__config__, _f, indent=2)
