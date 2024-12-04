import os

from clear_screen import clear


class Cleaner:
    @staticmethod
    def init():
        if "TERM" not in os.environ:
            os.environ["TERM"] = "xterm"

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear()
