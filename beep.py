import sys

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)


def beep():
    app.beep()
