class AccessibleChildrenNotFoundError(Exception):
    def __init__(self, focused_application: str):
        super().__init__(focused_application)
        self.focused_application = focused_application

    def __str__(self):
        return f"{self.focused_application} does not have any accessible elements."


class CouldNotFindAccessibleWindow(Exception):
    def __str__(self):
        return "The current window is not accessible."
