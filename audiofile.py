from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class AudioFile:
    def __init__(self):
        self.name = ""
        self.session = ""
        self.path = ""
        self.y = None
        self.sr = 0
        self.n_samples = 0
        self.tracked = False
        self.tempo = 0
        self.beat_samples = []
        self.volume_ratio = 1
        self.player = QMediaPlayer()

    def play(self):
        if self.player.state() == QMediaPlayer.PausedState:
            self.player.play()
        else:
            url = QUrl.fromLocalFile(self.path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
