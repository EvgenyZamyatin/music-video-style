from glob import glob
from time import time

import numpy as np
import colorsys

from scipy.misc import imread, imsave


def process(frames_dir, desc, model):
    return


def g(img, s_f):
    rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
    hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
    r, g, b = np.rollaxis(img, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    s *= s_f
    r, g, b = hsv_to_rgb(h, s, v)
    img = np.dstack((r, g, b))
    return img


def g1(img, s_f):
    return np.uint8(img * s_f)


def process_color(frames_dir, audio_analyze):
    for frame_file, f in zip(sorted(glob(frames_dir + '/*')), audio_analyze):
        img = imread(frame_file)
        img = g1(img, f)
        imsave(frame_file, img)
