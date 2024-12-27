from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy
from PIL import ImageGrab, ImageChops

from hints.backends.backend import HintsBackend
from hints.backends.exceptions import AccessibleChildrenNotFoundError
from hints.child import Child
import logging

if TYPE_CHECKING:
    from PIL.Image import Image

logger = logging.getLogger(__name__)


class OpenCV(HintsBackend):
    """OpenCV Hints Backend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend_name = "opencv"

    def screenshot(
        self, window_extents: tuple[int, int, int, int], invert: bool = False
    ) -> Image:
        """Take a screenshot of a window specified by its extents.

        :param window_extents: The extents of a window to screenshot.
        :param invert: Invert the image colors. This exists because
            image recognition yields better results with dark themes.
        :return: Screeshot image.
        """
        x, y, w, h = window_extents
        im = ImageGrab.grab(
            (
                x,
                y,
                x + w,
                y + h,
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
        window = self.get_active_window()

        if self.window_extents:
            application_rules = self.get_application_rules()
            gray_image = cv2.cvtColor(
                numpy.array(
                    self.screenshot(
                        self.window_extents,
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

            if self.window_extents:
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    children.add(
                        Child(
                            absolute_position=(
                                x + self.window_extents[0],
                                y + self.window_extents[1],
                            ),
                            relative_position=(x, y),
                            width=w,
                            height=h,
                        )
                    )

            logger.debug(
                "Finished gathering hints for '%s'",
                self.application_name,
            )

            if not children:
                raise AccessibleChildrenNotFoundError(window)

        return children
