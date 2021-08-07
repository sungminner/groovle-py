import librosa
import librosa.display
import soundfile
import IPython.display as ipd
import pydub
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_RATE = 44100


def mp3m4aRead(f):
    if f.split('.')[-1] == 'mp3':
        a = pydub.AudioSegment.from_mp3(f)
    else:
        a = pydub.AudioSegment.from_file(f)
    y = np.array(a.get_array_of_samples(), dtype=np.float32) / 2 ** 15

    if a.channels == 2:
        y = y.reshape((-1, 2))
        y1 = y[:, 0]
        y2 = y[:, 1]
        # 일단 스테레오면 왼쪽 음원만 활용 (평균 x)
        y = y1 # (y1 + y2) / 2

    if a.frame_rate < SAMPLE_RATE:
        return
    elif a.frame_rate > SAMPLE_RATE:
        resample = librosa.resample(y, a.frame_rate, SAMPLE_RATE)
        y, a.frame_rate = resample, SAMPLE_RATE

    return y, a.frame_rate


# read audio file
x, sr = mp3m4aRead('C:/Users/sm185/Desktop/code/python/groovle/audio/가요/10월의 날씨.mp3')

tempo, beat = librosa.beat.beat_track(x, sr=SAMPLE_RATE, start_bpm=150, units='time')

print(beat)
# approach 1 - onset detection and dynamic programming
# tempo, beat_samples = librosa.beat.beat_track(x, sr=SAMPLE_RATE, start_bpm=150, units='samples')
clicks = librosa.clicks(beat, sr=SAMPLE_RATE, length=len(x))
result = x + clicks
soundfile.write('beattracktest.wav', result, sr)
#
# plt.figure(figsize=(14, 5))
# librosa.display.waveplot(x, sr=SAMPLE_RATE, alpha=0.6)
# plt.vlines(beat_times, -1, 1, color='r')
# plt.ylim(-1, 1)
# plt.show()
