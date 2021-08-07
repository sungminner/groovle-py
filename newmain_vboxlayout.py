import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

# audio modules
from scipy.io.wavfile import write
import sounddevice as sd
from PyQt5.QtMultimedia import QMediaPlayer
import numpy as np

# pyplot modules
import librosa.display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import dates

# my modules
from audiofile import AudioFile
from merger import Merger, audioRead

SAMPLE_RATE = 44100


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.playlist = []
        self.player = QMediaPlayer()
        self.originalBPM = 0
        self.result = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Groovle")
        self.setWindowIcon(QIcon("icon.png"))
        # self.setStyleSheet("background-color: white")
        self.resize(1000, 800)
        self.center()
        self.statusBar().showMessage('Ready')

        MyCentralWidget = QWidget()
        self.setCentralWidget(MyCentralWidget)

        # 위젯 부분

        # vbox : 전체 레이아웃 박스
        vbox = QVBoxLayout()

        # sourcevbox : 음원 리스트 레이아웃 박스
        self.sourcevbox = QVBoxLayout()
        self.sourcehbox = []
        for i in range(3):
            self.sourcehbox.append(QHBoxLayout())

            name = QLabel("이미 슬픈 사랑.mp3")
            sessioncb = QComboBox()
            sessions = ['보컬', '기타', '키보드', '베이스', '드럼', '사용자 설정']
            sessioncb.addItems(sessions)
            playbtn = QPushButton()
            playbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            pausebtn = QPushButton()
            pausebtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            stopbtn = QPushButton()
            stopbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
            beattrackbtn = QPushButton("박자 분석")

            self.sourcehbox[i].addWidget(name)
            self.sourcehbox[i].addWidget(sessioncb)
            self.sourcehbox[i].addWidget(playbtn)
            self.sourcehbox[i].addWidget(pausebtn)
            self.sourcehbox[i].addWidget(stopbtn)
            self.sourcehbox[i].addWidget(beattrackbtn)

            self.sourcevbox.addLayout(self.sourcehbox[i])

        vbox.addLayout(self.sourcevbox)
        MyCentralWidget.setLayout(vbox)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyMainWindow()
    sys.exit(app.exec_())
