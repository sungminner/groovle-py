import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

SAMPLE_RATE = 44100


class BeatEditorWindow(QWidget):
    def __init__(self, audiofile):
        super().__init__()
        self.audiofile = audiofile
