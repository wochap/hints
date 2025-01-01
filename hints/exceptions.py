class WindowSystemNotSupported(Exception):
    def __init__(self, window_system_name: str):
        super().__init__()
        self.window_system_name = window_system_name

    def __str__(self):
        return f"'{self.window_system_name}' not supported please submit an issue at https://github.com/AlfredoSequeida/hints/issues."
