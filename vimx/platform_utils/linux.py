from json import loads
from subprocess import DEVNULL, PIPE, Popen
from typing import Tuple


def get_screen_resolution() -> Tuple[int, int]:
    """
    Gets the screen resolution using xrandar or swaymsg
    """
    try:
        output = Popen(
            r"xrandr  | grep \* | cut -d' ' -f4",
            shell=True,
            stdout=PIPE,
            stderr=DEVNULL,
        ).communicate()[0]
        w, h = output.decode("utf-8").strip().split("x")
        return (int(w), int(h))
    except:
        pass

    output = Popen(
        "swaymsg -t get_outputs",
        shell=True,
        stdout=PIPE,
        stderr=DEVNULL,
    ).communicate()[0]
    tmp = loads(output)[0]["current_mode"]

    resolution = "{w}x{h}".format(w=tmp["width"], h=tmp["height"])

    return resolution
