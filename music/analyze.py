
import numpy as np
from scipy.signal import savgol_filter

from utils import readAudioFile


def analyze(audio_file, frames_count):
    audio = readAudioFile(audio_file)
    audio = np.abs(audio)
    step = int(np.ceil(len(audio) / frames_count))
    fs = []
    for i in range(0, len(audio), step):
        fs.append(audio[i:i + step].mean())
    fs = np.array(fs)
    fs = (fs - fs.min()) / (fs.max() - fs.min())
    fs[fs < 0.8] /= 5
    fs[fs >= 0.8] *= 2
    fs = savgol_filter(fs, 7, 3)
    fs = (fs - fs.min()) / (fs.max() - fs.min())
    for i in range(1, len(fs)):
        if fs[i] > fs[i - 1]: continue
        fs[i] = max(fs[i], fs[i - 1] - 0.04)
    return fs