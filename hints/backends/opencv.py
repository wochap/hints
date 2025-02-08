from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import cv2
import numpy
import pyscreenshot as ImageGrab
from numpy import float32, ones, uint8
from PIL import ImageChops

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

    def get_children(self) -> list[Child]:
        """Get children.

        :return: Children.
        """
        children: list[Child] = []
        application_rules = self.get_application_rules()
        window_extents_offsets = (0, 0, 0, 0)

        match self.window_system.window_system_name:
            case "sway":
                # in sway, we need to exclude the top bar from the screenshot region
                window_extents_offsets = (0, self.window_system.bar_height, 0, 0)

        gray_image = cv2.cvtColor(
            numpy.array(
                self.screenshot(
                    self.window_system.focused_window_extents,
                    window_extents_offsets=window_extents_offsets,
                    invert=application_rules["invert_screenshot_colors"],
                )
            ),
            cv2.COLOR_BGR2GRAY,
        )

        edges = cv2.Canny(
            gray_image,
            application_rules["canny_min_val"],
            application_rules["canny_max_val"],
        )

        kernel = ones(
            (application_rules["kernel_size"], application_rules["kernel_size"]), uint8
        )

        dilated_edges = cv2.dilate(edges, kernel)

        contours, _ = cv2.findContours(
            dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            children.append(
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
