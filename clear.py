import os
from subprocess import call
from sys import platform

if "TERM" not in os.environ:

    def clear():
        pass

elif platform not in ("win32", "cygwin"):

    def clear():
        call("clear", shell=True)

else:

    def clear():
        call("cls", shell=True)
