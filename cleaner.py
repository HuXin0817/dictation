import os

from clear_screen import clear

if "TERM" not in os.environ:
    os.environ["TERM"] = "xterm"


class Cleaner:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear()
