from merger import audioRead
from scipy.io.wavfile import write

file = 'C:/Users/sm185/Desktop/code/python/groovle/audio/녹음/사랑한다는 말로도 위로가 되지 않는 - 키보드 메트로놈.m4a'

y, sr = audioRead(file)
write("resample.wav", sr, y)

