import librosa
import soundfile
import numpy as np
import pydub

SAMPLE_RATE = 44100


class Merger:
    def __init__(self, playlist, originalBPM):
        self.playlist = playlist
        self.originalBPM = originalBPM
        self.original_samples_per_block = SAMPLE_RATE * 60 / self.originalBPM

    def beat_adjust(self):
        for audiofile in self.playlist:
            # beat tracking
            tempo, beat_samples = librosa.beat.beat_track(audiofile.y,
                                                          sr=SAMPLE_RATE,
                                                          start_bpm=self.originalBPM,
                                                          units='samples')
            print(audiofile.name + " 박자 : " + str(tempo) + "BPM")
            beat_times = librosa.samples_to_time(beat_samples, sr=SAMPLE_RATE)
            clicks = librosa.clicks(beat_times, sr=SAMPLE_RATE, length=len(audiofile.y))
            result = audiofile.y + clicks
            soundfile.write('beattrack_' + audiofile.name + '.wav', result, SAMPLE_RATE)

            # time stretching TODO: 시작되지 않은 부분 자르기 - gui에서 박자 bar 클릭
            result = np.array([])

            block_first = audiofile.y[:beat_samples[0]]
            stretch_ratio = len(block_first) / self.original_samples_per_block
            block_str_first = librosa.effects.time_stretch(block_first, stretch_ratio)
            result = np.append(result, block_str_first)

            for i in range(len(beat_samples) - 1):
                block = audiofile.y[beat_samples[i]:beat_samples[i + 1]]
                stretch_ratio = len(block) / self.original_samples_per_block
                block_str = librosa.effects.time_stretch(block, stretch_ratio)
                result = np.append(result, block_str)

            block_last = audiofile.y[beat_samples[-1]:]
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
            result = audioRead(audiofile.path)
            if result == 'e1':
                print(audiofile.name + " 파일은 sampling rate가 낮아 음질에 영향을 줄 수 있으니 다시 녹음하시기 바랍니다.")
                return
            elif result == 'e2':
                print(audiofile.name + ': 지원하지 않는 파일 형식입니다.')
                return
            audiofile.y, audiofile.sr = result
            audiofile.n_samples = len(audiofile.y)

        self.beat_adjust()
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
