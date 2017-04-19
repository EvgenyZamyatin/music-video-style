import subprocess
import subprocess as sp
import numpy as np
import sys
from scipy.misc import imread, imresize

PROBE = 'ffprobe'
# PROBE = 'avprobe'
FFMPEG = 'ffmpeg'
# FFMPEG = 'avconv'

AUDIO_DUR_CMD = '%s -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s'


def get_fps(video_file):
    return subprocess.check_output('%s -v 0 -of compact=p=0 -select_streams 0 '
                                   '-show_entries stream=r_frame_rate '
                                   '-of default=noprint_wrappers=1:nokey=1 %s' % (PROBE, video_file),
                                   shell=True).decode()[:-1]


def extract_frames(video_file, out_dir):
    subprocess.call('%s -i %s %s/%%05d.jpg' % (FFMPEG, video_file, out_dir), shell=True)


def extract_audio(video_file, out_file):
    subprocess.call('%s -i %s %s' % (FFMPEG, video_file, out_file), shell=True)


def construct_video(frames_dir, audio_file, fps, out_file):
    subprocess.call('%s -y -start_number 1 -i %s/%%05d.jpg -i %s -c:v libx264 -r %s '
                    '-pix_fmt yuv420p -c:a aac -strict experimental -shortest %s' % (
                        FFMPEG, frames_dir, audio_file, fps, out_file),
                    shell=True)


def readAudioFile(filename):
    command = [FFMPEG,
               '-i', filename,
               '-f', 's16le',
               '-acodec', 'pcm_s16le',
               '-ar', '44100',
               '-ac', '1',
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


def load_and_resize(img, size=None, center_crop=True):
    try:
        img = imread(img, mode="RGB")
    except OSError as e:
        print(e)
        sys.exit(1)

    if center_crop:
        # Extract a square crop from the center of the image.
        cur_shape = img.shape[:2]
        shorter_side = min(cur_shape)
        longer_side_xs = max(cur_shape) - shorter_side
        longer_side_start = int(longer_side_xs / 2.)
        longer_side_slice = slice(longer_side_start, longer_side_start + shorter_side)
        if shorter_side == cur_shape[0]:
            img = img[:, longer_side_slice, :]
        else:
            img = img[longer_side_slice, :, :]

    if size is not None:
        # Resize the image.
        cur_shape = img.shape[:2]
        shorter_side = min(cur_shape)
        aspect = max(cur_shape) / float(shorter_side)
        new_shorter_side = int(size / aspect)
        if shorter_side == cur_shape[0]:
            new_shape = (new_shorter_side, size)
        else:
            new_shape = (size, new_shorter_side)
        img = imresize(img, new_shape)
    return img
