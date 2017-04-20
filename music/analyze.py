import sys
sys.path.append('.')
import argparse
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


def analyze_1(audio_file, frames_count):
    audio = readAudioFile(audio_file)
    audio = np.abs(audio)
    step = int(np.ceil(len(audio) / frames_count))
    fs = []
    for i in range(0, len(audio), step):
        chunk = audio[i:i + step]
        fft = np.fft.fft(chunk, 2048)
        t = np.absolute(fft)
        t = (t[:len(t)//2] + (t[len(t)//2:])) / 2
        fs.append(np.trapz(t[8:14]))
    fs = np.array(fs)
    #fs = (fs - fs.min()) / (fs.max() - fs.min())
    #fs[fs < 0.7] /= 5
    #fs[fs >= 0.7] *= 2
    #fs = savgol_filter(fs, 7, 3)
    fs = savgol_filter(fs, 9, 5)
    fs = (fs-fs.mean()) / np.sqrt(fs.var() + 1e-5)
    fs[fs < 0] = 0
    #fs = savgol_filter(fs, 5, 3)
    fs = (fs - fs.mean()) / np.sqrt(fs.var() + 1e-5)
    fs[fs < 0] = 0
    fs = (fs - fs.min()) / (fs.max() - fs.min())

    for i in range(1, len(fs)):
        if fs[i] > fs[i - 1]: continue
        fs[i] = max(fs[i], fs[i - 1] - 0.035)

    for i in range(0, len(fs)-1):
        if fs[i+1] < fs[i]: continue
        fs[i+1] = min(fs[i] + 0.035, fs[i + 1])

    #fs = savgol_filter(fs, 3, 1)
    #fs = (fs - fs.mean())
    #fs[fs < 0] = 0
    #fs = (fs - fs.min()) / (fs.max() - fs.min())

    return fs


def main(args):
    audio_analyze = analyze(args.audio, args.frames)
    import matplotlib.pyplot as plt
    plt.plot(audio_analyze)
    plt.show()


if __name__ == '__main__':
    main_arg_parser = argparse.ArgumentParser()
    main_arg_parser.add_argument("--audio", "-a", type=str, required=True, help='Path to audio file')
    main_arg_parser.add_argument("--frames", "-f", type=int, required=True, help='Frames count')
    main(main_arg_parser.parse_args())
