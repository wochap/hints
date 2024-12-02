class AccessibleChildrenNotFoundError(Exception):
    def __init__(self, active_window):
        self.active_window = active_window
        super().__init__(active_window)

    def __str__(self):
        return f"{self.active_window} does not have any accessible elements."


class CouldNotFindAccessibleWindow(Exception):
    def __str__(self):
        return "The current window is not accessible."
