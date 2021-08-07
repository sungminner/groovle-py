import librosa
import librosa.display
import soundfile
import IPython.display as ipd
import pydub
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_RATE = 44100
ORIGINAL_BPM = 183
ORIGINAL_SAMPLES_PER_BLOCK = SAMPLE_RATE * 60 / ORIGINAL_BPM


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
        y = y1  # (y1 + y2) / 2

    if a.frame_rate < SAMPLE_RATE:
        return
    elif a.frame_rate > SAMPLE_RATE:
        resample = librosa.resample(y, a.frame_rate, SAMPLE_RATE)
        y, a.frame_rate = resample, SAMPLE_RATE

    return y, a.frame_rate


# read audio file
y, sr = mp3m4aRead('C:/Users/sm185/Desktop/code/python/groovle/audio/피아노 - ANIMA.m4a')

# beat tracking
tempo, beat_samples = librosa.beat.beat_track(y, sr=SAMPLE_RATE, start_bpm=ORIGINAL_BPM, units='samples')
print(tempo)
beat_times = librosa.samples_to_time(beat_samples, sr=SAMPLE_RATE)
clicks = librosa.clicks(beat_times, sr=SAMPLE_RATE, length=len(y))
result = y + clicks
soundfile.write('beattrack.wav', result, SAMPLE_RATE)

# time stretching
result = np.array([])
for i in range(len(beat_samples) - 1):
    block = y[beat_samples[i]:beat_samples[i + 1]]
    stretch_ratio = len(block) / ORIGINAL_SAMPLES_PER_BLOCK
    block_str = librosa.effects.time_stretch(block, stretch_ratio)
    result = np.append(result, block_str)

soundfile.write('stretched.wav', result, SAMPLE_RATE)

# plot
plt.figure(figsize=(14, 5))
librosa.display.waveplot(y, sr=SAMPLE_RATE, alpha=0.6)
plt.vlines(beat_times, -1, 1, color='r')
plt.ylim(-1, 1)
plt.show()
