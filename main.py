import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

# audio modules
import librosa
from scipy.io.wavfile import write
import sounddevice as sd
from PyQt5.QtMultimedia import QMediaPlayer
import numpy as np

# display modules
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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
        self.selectedrow = None
        self.result = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Groovle")
        self.setWindowIcon(QIcon("icon.png"))
        # self.setStyleSheet("background-color: white")
        self.resize(1500, 900)
        self.center()
        self.statusBar().showMessage('Ready')

        MyCentralWidget = QWidget()
        self.setCentralWidget(MyCentralWidget)

        # 위젯 부분
        # bpminputhbox : BPM 입력 버튼 레이아웃 박스
        bpminputhbox = QHBoxLayout()

        BPMlabel = QLabel('원곡 BPM (30 ~ 240의 정수) : ')
        getBPM = QSpinBox()
        getBPM.setRange(30, 240)

        getBPM.valueChanged.connect(self.setBPM)

        bpminputhbox.addStretch(1)
        bpminputhbox.addWidget(BPMlabel)
        bpminputhbox.addWidget(getBPM)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('파일명'))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('세션'))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem('박자 분석'))
        self.table.setHorizontalHeaderItem(3, QTableWidgetItem('한 박자 앞으로'))
        self.table.setHorizontalHeaderItem(4, QTableWidgetItem('한 박자 뒤로'))

        # read only
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # single row selection
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # drag and drop TODO: 테이블만 드래그 앤 드롭 되도록 하기
        self.setAcceptDrops(True)
        # stretch last column
        self.table.horizontalHeader().setStretchLastSection(True)

        # # 클릭된 음원을 그래프로 plot
        # self.table.itemClicked.connect(self.showSourceGraph)

        # table.itemSelectionChanged.connect(tableChanged)
        # table.itemDoubleClicked.connect(tableDbClicked)

        # header = self.table.horizontalHeader()
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # self.table.setColumnWidth(0, int(self.table.width() * 0.7))
        # self.table.setColumnWidth(1, int(self.table.width() * 0.3))
        # print(self.table.width())

        # vbox : 전체 레이아웃 박스
        vbox = QVBoxLayout()

        # hbox1 : 업로드, 삭제, 전체삭제 버튼 레이아웃 박스
        hbox1 = QHBoxLayout()

        uploadButton = QPushButton('업로드')
        deleteButton = QPushButton('삭제')
        deleteAllButton = QPushButton('전체삭제')
        mergeButton = QPushButton('합성')

        uploadButton.clicked.connect(self.upload)
        deleteButton.clicked.connect(self.delete)
        deleteAllButton.clicked.connect(self.deleteAll)
        mergeButton.clicked.connect(self.merge)

        hbox1.addStretch(1)
        hbox1.addWidget(uploadButton)
        hbox1.addWidget(deleteButton)
        hbox1.addWidget(deleteAllButton)
        hbox1.addWidget(mergeButton)
        hbox1.addStretch(1)

        # self.graphgroupbox : 그래프 관련 메뉴 그룹박스
        self.graphgroupbox = QGroupBox('그래프')
        graphvbox = QVBoxLayout()
        # playhbox : 재생, 일시정지, 중지 버튼 레이아웃
        playhbox = QHBoxLayout()

        self.graphlineedit = QLineEdit()
        self.graphlineedit.setReadOnly(True)
        # graphlineedit 내용 바꾸는 코드는 self.showSourceGraph 있음

        graphplaybtn = QPushButton()
        graphplaybtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        graphpausebtn = QPushButton()
        graphpausebtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        graphstopbtn = QPushButton()
        graphstopbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        graphplaybtn.clicked.connect(self.graphplay)
        graphpausebtn.clicked.connect(self.graphpause)
        graphstopbtn.clicked.connect(self.graphstop)

        playhbox.addWidget(self.graphlineedit)
        playhbox.addWidget(graphplaybtn)
        playhbox.addWidget(graphpausebtn)
        playhbox.addWidget(graphstopbtn)
        playhbox.addStretch(1)

        # matplotlib 그려질 부분
        self.fig = plt.Figure(figsize=(2, 2))  # figsize는 첫번째 숫자는 의미 없고 두 번째 숫자에 따라 높이 변함
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(1, 1, 1)
        # TODO: grid 사용할지 축 아예 없앨지 정하기
        self.ax.grid()
        self.ax.axis('off')

        graphvbox.addLayout(playhbox)
        graphvbox.addWidget(self.canvas)
        self.graphgroupbox.setLayout(graphvbox)

        # self.resultgroupbox : 합성 결과물 관련 메뉴 그룹박스
        self.resultgroupbox = QGroupBox('합성 결과')
        self.resultgroupbox.setEnabled(False)

        mvbox = QVBoxLayout()
        mhbox1 = QHBoxLayout()
        mhbox2 = QHBoxLayout()

        # sourcelist : 어떤 소스를 합성했는지 보여 주는 문자열
        sourcelabel = QLabel('Source: ')
        self.sourcelineedit = QLineEdit()
        self.sourcelineedit.setReadOnly(True)

        mplaybtn = QPushButton()
        mplaybtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        mpausebtn = QPushButton()
        mpausebtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        mstopbtn = QPushButton()
        mstopbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        saveButton = QPushButton('저장')

        mplaybtn.clicked.connect(self.mplay)
        mpausebtn.clicked.connect(self.mpause)
        mstopbtn.clicked.connect(self.mstop)
        saveButton.clicked.connect(self.msave)

        mhbox1.addWidget(sourcelabel)
        mhbox1.addWidget(self.sourcelineedit)

        mhbox2.addStretch(1)
        mhbox2.addWidget(mplaybtn)
        mhbox2.addWidget(mpausebtn)
        mhbox2.addWidget(mstopbtn)
        mhbox2.addWidget(saveButton)
        mhbox2.addStretch(1)

        mvbox.addLayout(mhbox1)
        mvbox.addLayout(mhbox2)

        self.resultgroupbox.setLayout(mvbox)

        vbox.addLayout(bpminputhbox)
        vbox.addWidget(self.table)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.graphgroupbox)
        vbox.addWidget(self.resultgroupbox)
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
                                             'Sound (*.wav *.flac *.ogg *.mp3 *.m4a)')
        cnt = len(files[0])
        filelist = []

        if len(self.playlist) + cnt > 10:
            print('10개 이상의 파일을 업로드할 수 없습니다.')
        else:
            for i in range(cnt):
                filelist.append(AudioFile())
                filelist[i].name = files[0][i].split('/')[-1]
                filelist[i].path = files[0][i]
            self.playlist = self.playlist + filelist
            self.showPlaylist()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        cnt = len(files)
        filelist = []

        if len(self.playlist) + cnt > 10:
            print('10개 이상의 파일을 업로드할 수 없습니다.')
        else:
            for i in range(cnt):
                ext = files[i].split('.')[-1]
                if ext == 'wav' or ext == 'flac' or ext == 'ogg' or ext == 'mp3' or ext == 'm4a':
                    filelist.append(AudioFile())
                    filelist[i].name = files[i].split('/')[-1]
                    filelist[i].path = files[i]
                else:
                    print(files[i].split('/')[-1] + ': 지원하지 않는 파일 형식입니다.')
                    return
            self.playlist = self.playlist + filelist
            self.showPlaylist()

    def delete(self):
        self.ax.clear()
        index = []
        for item in self.table.selectedIndexes():
            index.append(item.row())
        index = list(set(index))
        index.reverse()
        for i in index:
            self.playlist.pop(i)
        self.showPlaylist()

    def deleteAll(self):
        self.ax.clear()
        self.playlist.clear()
        self.showPlaylist()

    def graphplay(self):
        # TODO: 재생할 때 클릭 음원을 포함할지 안할지 선택할 수 있도록 하기(토글)
        # TODO: 해당 음원 파일 삭제하고 재생 누르면 버그
        if self.selectedrow is None:
            print('재생할 음원의 그래프를 그려야 합니다!')
            return
        sd.play(self.playlist[self.selectedrow].y, SAMPLE_RATE)

    def graphpause(self):
        pass

    def graphstop(self):
        if self.selectedrow is None:
            print('재생할 음원의 그래프를 그려야 합니다!')
            return
        sd.stop()

    def showSourceGraph(self, i):
        self.ax.clear()
        audiofile = self.playlist[i]
        print(audiofile.name + '의 그래프를 그리는 중...')

        self.selectedrow = i

        sec = np.array(range(audiofile.n_samples)) / SAMPLE_RATE
        self.ax.plot(sec, audiofile.y)

        # TODO: sec array가 소수여서 mm:ss 형태로 표현되지 않음. 방법 찾기 전까지는 초로 표시
        # formatter = dates.DateFormatter('%M:%S')
        # ax.xaxis.set_major_formatter(formatter)

        self.canvas.draw()

        self.graphlineedit.setText(self.playlist[self.selectedrow].name)
        if audiofile.tracked:
            beattrackcompbtn = QPushButton("그래프 열기")
            beattrackcompbtn.clicked.connect(lambda s, index=i: self.showSourceGraph(index))
            self.table.setCellWidget(i, 2, beattrackcompbtn)

        print(audiofile.name + '의 그래프 그리기 완료')

    def beatTrack(self, i):
        # TODO: 박자 분석 누르면 새 창으로 해서 수동으로 커서 수정하게 하기 - 프리토타이핑 쓸때
        print('row: ' + str(i))
        audiofile = self.playlist[i]

        self.selectedrow = i

        if self.originalBPM == 0:
            print('원곡의 BPM을 먼저 입력하세요')
            return
        if audiofile.tracked:  # 박자 분석이 되었다는 건 파일을 열어서 변수에 저장했다는 의미 (한번에 두 개를 하므로)
            print('박자 분석이 완료된 파일입니다.')
            self.showSourceGraph(i)
            return

        audiofile.y, audiofile.sr = audioRead(audiofile.path)  # TODO: e1, e2 오류 처리
        audiofile.n_samples = len(audiofile.y)
        self.showSourceGraph(i)

        tempo, beat_samples = librosa.beat.beat_track(audiofile.y,
                                                      sr=SAMPLE_RATE,
                                                      start_bpm=self.originalBPM,
                                                      units='samples')
        audiofile.tempo, audiofile.beat_samples = tempo, beat_samples
        audiofile.tracked = True

        if audiofile.tracked:
            graphopenbtn = QPushButton("그래프 열기")
            graphopenbtn.clicked.connect(lambda s, index=i: self.showSourceGraph(index))
            self.table.setCellWidget(i, 2, graphopenbtn)

        # 아래는 임시 확인용
        beat_times = librosa.samples_to_time(audiofile.beat_samples, sr=SAMPLE_RATE)
        clicks = librosa.clicks(beat_times, sr=SAMPLE_RATE, length=len(audiofile.y))
        result = audiofile.y + clicks
        write('audio/tracked_result/beattrack_' + audiofile.name + '.wav', SAMPLE_RATE, result)

        # 박자마다 수직선 그리기
        #  for beat in audiofile.beat_samples:
        #      self.ax.axvline(beat, color='red')
        # self.canvas.draw()

        print(audiofile.name + " 박자 : " + str(audiofile.tempo) + "BPM")
        print('beat track completed')
        print('')

    def beatforward(self, i):
        self.selectedrow = i
        audiofile = self.playlist[i]
        if audiofile.tracked:
            audiofile.y = audiofile.y[audiofile.beat_samples[0]:]
            audiofile.beat_samples = audiofile.beat_samples - audiofile.beat_samples[0]
            audiofile.beat_samples = audiofile.beat_samples[1:]
            audiofile.n_samples = len(audiofile.y)
            print('한 박자 앞으로 이동 완료')
            # TODO: 한번에 한박자씩 말고 커서를 이용해서 어떤 박자에서 시작할지를 저장하기 (그래프 ui 개선 후)
        else:
            print('박자 분석을 먼저 진행하세요!')
        self.showSourceGraph(i)

    def beatbackward(self, i):
        self.selectedrow = i
        audiofile = self.playlist[i]
        if audiofile.tracked:
            padding = np.zeros(2048)
            audiofile.y = np.append(padding, audiofile.y)
            audiofile.beat_samples = audiofile.beat_samples + 2048
            audiofile.beat_samples = np.append(2048, audiofile.beat_samples)
            audiofile.n_samples = len(audiofile.y)
            print('한 박자 뒤로 이동 완료')
        else:
            print('박자 분석을 먼저 진행하세요!')
        self.showSourceGraph(i)

    def setBPM(self, bpm):
        self.originalBPM = bpm
        print(self.originalBPM)

    def merge(self):
        if len(self.playlist) == 0 or self.originalBPM == 0:
            return
        merger = Merger(self.playlist, self.originalBPM)
        merger.playlist = self.playlist
        self.result = merger.merge()

        if self.result is None:
            self.resultgroupbox.setEnabled(False)
        else:
            sourcelist = ', '.join([audiofile.name for audiofile in self.playlist])
            self.sourcelineedit.setText(sourcelist)
            self.resultgroupbox.setEnabled(True)

        print('합성 완료')
        # self.statusBar().showMessage('Completed')

    def showPlaylist(self):
        self.table.setRowCount(len(self.playlist))
        for i in range(len(self.playlist)):
            sessionbox = QComboBox()
            sessions = ['보컬', '기타', '키보드', '베이스', '드럼', '사용자 설정']
            sessionbox.addItems(sessions)
            sessionbox.currentIndexChanged.connect(lambda sindex, index=i: self.setSession(sindex, index))
            # sessionbox.setEditable(True)

            graphopenbtn = QPushButton("그래프 열기")
            beattrackbtn = QPushButton("박자 분석")
            beatforwardbtn = QPushButton("한 박자 앞으로")
            beatbackwardbtn = QPushButton("한 박자 뒤로")

            graphopenbtn.clicked.connect(lambda s, index=i: self.showSourceGraph(index))
            beattrackbtn.clicked.connect(lambda s, index=i: self.beatTrack(index))
            beatforwardbtn.clicked.connect(lambda s, index=i: self.beatforward(index))
            beatbackwardbtn.clicked.connect(lambda s, index=i: self.beatbackward(index))

            self.table.setItem(i, 0, QTableWidgetItem(self.playlist[i].name))
            self.table.setCellWidget(i, 1, sessionbox)
            if self.playlist[i].tracked:
                self.table.setCellWidget(i, 2, graphopenbtn)
            else:
                self.table.setCellWidget(i, 2, beattrackbtn)
            self.table.setCellWidget(i, 3, beatforwardbtn)
            self.table.setCellWidget(i, 4, beatbackwardbtn)
            print(self.playlist[i].name)
        print("")

    def setSession(self, sindex, index):
        sessions = ['보컬', '기타', '키보드', '베이스', '드럼', '사용자 설정']
        self.playlist[index].session = sessions[sindex]
        print(self.playlist[index].name, self.playlist[index].session)
        print("")

    def mplay(self):
        sd.play(self.result, SAMPLE_RATE)

    def mpause(self):
        pass

    def mstop(self):
        sd.stop()

    def msave(self):
        filename = getFileName()
        filesave = QFileDialog.getSaveFileName(self, 'save file', filename, 'wav files (*.wav)')
        if filesave[0] != "":
            write(filesave[0], SAMPLE_RATE, self.result)
        print("Save Completed")


def getFileName():
    with open("cnt.txt", "r+") as f:
        cnt = f.read()
        if cnt == "":
            f.write("1")
            cnt = "1"
        filename = "groovle_result_" + cnt + ".wav"
        cnt = int(cnt) + 1
        f.seek(0)
        f.truncate()
        f.write(str(cnt))

    return filename


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyMainWindow()
    sys.exit(app.exec_())
