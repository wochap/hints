from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import cv2
import numpy
<<<<<<< Updated upstream
from PIL import ImageChops, ImageGrab
=======
import pyscreenshot as ImageGrab
from PIL import ImageChops
>>>>>>> Stashed changes

from hints.backends.backend import HintsBackend
from hints.backends.exceptions import AccessibleChildrenNotFoundError
from hints.child import Child

if TYPE_CHECKING:
    from PIL.Image import Image

logger = logging.getLogger(__name__)


class OpenCV(HintsBackend):
    """OpenCV Hints Backend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend_name = "opencv"

    def screenshot(
        self,
        window_extents: tuple[int, int, int, int],
        window_extents_offsets: tuple[int, int, int, int] = (0, 0, 0, 0),
        invert: bool = False,
    ) -> Image:
        """Take a screenshot of a window specified by its extents.

        :param window_extents: The extents of a window to screenshot
            (x,y,width,height).
        :param window_extents_offsets: Any offsets for the screenshot
            area (window) (x,y,width,height).
        :param invert: Invert the image colors. This exists because
            image recognition yields better results with dark themes.
        :return: Screeshot image.
        """
        print(window_extents)
        x, y, w, h = window_extents
        im = ImageGrab.grab(
            (
                x + window_extents_offsets[0],
                y + window_extents_offsets[1],
                x + w + window_extents_offsets[2],
                y + h + window_extents_offsets[3],
            )
        )
        if invert:
            im = ImageChops.invert(im)
        return im

    def get_children(self) -> set[Child]:
        """Get children.

        :return: Children.
        """
        children = set()
<<<<<<< Updated upstream

        application_rules = self.get_application_rules()
=======
        application_rules = self.get_application_rules()
        window_extents_offsets = (0, 0, 0, 0)

        match self.window_system.window_system_name:
            case "sway":
                # in sway, we need to exclude the top bar from the screenshot region
                window_extents_offsets = (0, self.window_system.bar_height, 0, 0)

>>>>>>> Stashed changes
        gray_image = cv2.cvtColor(
            numpy.array(
                self.screenshot(
                    self.window_system.focused_window_extents,
<<<<<<< Updated upstream
=======
                    window_extents_offsets=window_extents_offsets,
>>>>>>> Stashed changes
                    invert=application_rules["invert_screenshot_colors"],
                )
            ),
            cv2.COLOR_BGR2GRAY,
        )

        _, thresh = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            children.add(
                Child(
                    absolute_position=(
                        x + self.window_system.focused_window_extents[0],
                        y + self.window_system.focused_window_extents[1],
                    ),
                    relative_position=(x, y),
                    width=w,
                    height=h,
                )
            )

        logger.debug(
            "Finished gathering hints for '%s'",
            self.window_system.focused_applicaiton_name,
        )

        if not children:
            raise AccessibleChildrenNotFoundError(
                self.window_system.focused_applicaiton_name
            )

        return children
