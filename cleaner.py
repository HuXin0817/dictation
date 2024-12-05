import os

from clear_screen import clear

if "TERM" not in os.environ:
    os.environ["TERM"] = "xterm"
