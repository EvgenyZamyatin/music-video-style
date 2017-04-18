from glob import glob
from time import time

import numpy as np
import colorsys

from scipy.misc import imread, imsave
import theano

from style.fast_neural_style.transformer_net import get_transformer_net
from style.utils import floatX, load_and_preprocess_img, deprocess_img_and_save

model_pool = {}


class NeuralModel:
    def __init__(self, model_path, size):
        self.size = size
        self.X = theano.shared(np.array([[[[]]]], dtype=floatX))
        weights = model_path
        transformer_net = get_transformer_net(self.X, weights)
        Xtr = transformer_net.output
        self.get_Xtr = theano.function([], Xtr)

    def magic(self, image_batch):
        inplace = False
        if isinstance(image_batch, list) and isinstance(image_batch[0], str):
            inplace = True
        processed = []
        for img in image_batch:
            img = load_and_preprocess_img(img, self.size)
            processed.append(img)
        processed = np.array(processed, dtype=floatX)
        self.X.set_value(processed)
        output_batch = self.get_Xtr()
        if inplace:
            for img, file in zip(output_batch, image_batch):
                deprocess_img_and_save(img, file)
            return

        deprocessed = []
        for img in output_batch:
            img = deprocess_img_and_save(img)
            deprocessed.append(img)
        deprocessed = np.array(deprocessed, dtype=deprocessed[0].dtype)
        return deprocessed


def process(frames_dir, desc, model, size):
    if model not in model_pool:
        model_pool[model] = NeuralModel(model, size)
    model = model_pool[model]
    frame_files = sorted(glob(frames_dir + '/*'))
    assert len(desc) == len(frame_files)
    for i in range(0, len(desc), 10):
        frame_batch = frame_files[i:i + 10]
        desc_batch = desc[i:i + 10]
        model.magic(frame_batch)


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
