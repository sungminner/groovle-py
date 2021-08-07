import librosa
import matplotlib.pyplot as plt
from merger import audioRead


path = input('path: ')
BPM = int(input('BPM: '))

name = path.split('/')[-1].split('.')[0]
SAMPLE_RATE = 44100
SAMPLES_PER_BLOCK = SAMPLE_RATE * 60 / BPM  # 원래 박자당 샘플 수

y, sr = audioRead(path)
tempo, beat_samples = librosa.beat.beat_track(y,
                                              sr=SAMPLE_RATE,
                                              start_bpm=BPM,
                                              units='samples')
midpoint = []
real_BPM = []
for i in range(15, len(beat_samples) - 1):
    midpoint.append((beat_samples[i] + beat_samples[i + 1]) / 2 / SAMPLE_RATE)
    real = (beat_samples[i + 1] - beat_samples[i]) / SAMPLES_PER_BLOCK * BPM
    real_BPM.append(real)

plt.plot(midpoint, real_BPM)
plt.savefig('beatguide/beatguide_' + name + '.png')
plt.show()
