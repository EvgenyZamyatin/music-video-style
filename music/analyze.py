import subprocess as sp

import numpy as np
from scipy.signal import savgol_filter


def readAudioFile(filename):
    command = ['ffmpeg',
               '-i', filename,
               '-f', 's16le',
               '-acodec', 'pcm_s16le',
               '-ar', '44100',  # ouput will have 44100 Hz
               '-ac', '1',  # mono (set to '2' for stereo)
               '-']
    in_pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=10 ** 8)
    completeAudioArray = np.empty(0, dtype="int16")
    while True:
        raw_audio = in_pipe.stdout.read(88200 * 4)
        if len(raw_audio) == 0:
            break
        audio_array = np.fromstring(raw_audio, dtype="int16")
        completeAudioArray = np.append(completeAudioArray, audio_array)
    in_pipe.kill()
    in_pipe.wait()
    return completeAudioArray


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