import librosa
import numpy as np
import pydub

SAMPLE_RATE = 44100


class Merger:
    def __init__(self, playlist, originalBPM):
        self.playlist = playlist
        self.originalBPM = originalBPM
        self.original_samples_per_block = SAMPLE_RATE * 60 / self.originalBPM

    def time_stretch(self, audiofile):
        result = np.array([])

        block_first = audiofile.y[:audiofile.beat_samples[0]]
        stretch_ratio = len(block_first) / self.original_samples_per_block
        block_str_first = librosa.effects.time_stretch(block_first, stretch_ratio)
        result = np.append(result, block_str_first)

        for i in range(len(audiofile.beat_samples) - 1):
            block = audiofile.y[audiofile.beat_samples[i]:audiofile.beat_samples[i + 1]]
            stretch_ratio = len(block) / self.original_samples_per_block
            block_str = librosa.effects.time_stretch(block, stretch_ratio)
            result = np.append(result, block_str)

        block_last = audiofile.y[audiofile.beat_samples[-1]:]
        stretch_ratio = len(block_last) / self.original_samples_per_block
        block_str_last = librosa.effects.time_stretch(block_last, stretch_ratio)
        result = np.append(result, block_str_last)

        audiofile.y = result
        audiofile.n_samples = len(result)

    def match_len(self):
        file_len_array = []
        for audiofile in self.playlist:
            file_len_array.append(audiofile.n_samples)
        max_len = max(file_len_array)
        for audiofile in self.playlist:
            padding = np.zeros(max_len - len(audiofile.y))
            audiofile.y = np.hstack((audiofile.y, padding))

    def merge(self):
        for audiofile in self.playlist:
            if not audiofile.tracked:  # TODO: 첫 박자 설정하는 코드 완성한 다음에는 첫 박자가 설정됐는지를 기준으로 하기
                print('모든 파일의 박자 분석을 먼저 해야 합니다!')
                return

        for audiofile in self.playlist:
            print(audiofile.name + " BPM : " + str(audiofile.tempo))

            self.time_stretch(audiofile)

        self.match_len()

        merged = 0
        for audiofile in self.playlist:
            merged = merged + audiofile.y
        merged = merged / len(self.playlist)
        merged32 = merged.astype(np.float32)
        return merged32


def audioRead(path):
    ext = path.split('.')[-1]
    if ext == 'wav' or ext == 'flac' or ext == 'ogg':
        y, sr = librosa.load(path, sr=SAMPLE_RATE, mono=True)
        return y, sr
    elif ext == 'mp3' or ext == 'm4a':
        if ext == 'mp3':
            a = pydub.AudioSegment.from_mp3(path)
        else:
            a = pydub.AudioSegment.from_file(path)
        y = np.array(a.get_array_of_samples(), dtype=np.float32) / 2 ** 15

        if a.channels == 2:
            y = y.reshape((-1, 2))
            y1 = y[:, 0]
            y2 = y[:, 1]
            # 일단 스테레오면 왼쪽 음원만 활용 (평균 x)
            y = y1  # (y1 + y2) / 2

        if a.frame_rate < SAMPLE_RATE:
            return 'e1'
        elif a.frame_rate > SAMPLE_RATE:
            resample = librosa.resample(y, a.frame_rate, SAMPLE_RATE)
            y, a.frame_rate = resample, SAMPLE_RATE

        return y, a.frame_rate
    else:
        return 'e2'
