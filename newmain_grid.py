import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import player
import oldmerge as mg


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.playlist = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Groovle")
        self.setWindowIcon(QIcon("icon.png"))
        # self.setStyleSheet("background-color: white")
        self.resize(500, 500)
        self.center()
        self.statusBar().showMessage('Ready')

        MyCentralWidget = QWidget()
        self.setCentralWidget(MyCentralWidget)

        vbox = QVBoxLayout()

        # 그리드 부분
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(QLabel('파일명'), 0, 0)
        self.grid.addWidget(QLabel('세션'), 0, 1)
        self.grid.addWidget(QLabel('Play Control'), 0, 2)

        hbox = QHBoxLayout()
        uploadButton = QPushButton('업로드')
        deleteButton = QPushButton('삭제')
        deleteAllButton = QPushButton('전체삭제')
        mergeButton = QPushButton('합성')
        uploadButton.clicked.connect(self.upload)
        deleteButton.clicked.connect(self.delete)
        deleteAllButton.clicked.connect(self.deleteAll)
        mergeButton.clicked.connect(self.merge)

        hbox.addStretch(1)
        hbox.addWidget(uploadButton)
        hbox.addWidget(deleteButton)
        hbox.addWidget(deleteAllButton)
        hbox.addWidget(mergeButton)
        hbox.addStretch(1)

        vbox.addLayout(self.grid)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        MyCentralWidget.setLayout(vbox)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def upload(self):
        files = QFileDialog.getOpenFileNames(self,
                                             'Select one or more files to open',
                                             '',
                                             'Sound (*.wav *.mp3 *.m4a *.ogg *.flac *.wma)')
        cnt = len(files[0])

        if len(self.playlist) + cnt > 10:
            print('10개 이상의 파일을 업로드할 수 없습니다.')
        else:
            self.playlist = self.playlist + files[0]
            self.showPlaylist()

    def delete(self):
        index = []
        for item in self.table.selectedIndexes():
            index.append(item.row())

        index = list(set(index))
        index.reverse()

        for i in index:
            self.playlist.pop(i)
        print(index)

        self.showPlaylist()

    def deleteAll(self):
        self.playlist.clear()
        self.showPlaylist()

    def merge(self):
        mg.merge(self.playlist)
        self.statusBar().showMessage('Completed')

    def showPlaylist(self):
        for i in range(len(self.playlist)):
            f_name = self.playlist[i].split('/')[-1]
            self.grid.addWidget(QLabel(f_name), i + 1, 0)
            self.grid.addWidget(QLabel("session"), i + 1, 1)
            self.grid.addWidget(QLabel("play"), i + 1, 2)
            print(f_name)
        print("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyMainWindow()
    sys.exit(app.exec_())
