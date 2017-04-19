import argparse
import os
from glob import glob

import uuid

from shutil import rmtree

from music.analyze import analyze
from style.stylish import process
import subprocess

from utils import get_fps, extract_frames, extract_audio, construct_video


def main(args):
    uid = uuid.uuid1()
    dir_name = './.TEMP-' + str(uid)
    os.makedirs(dir_name)

    audio_file = dir_name + '/audio.mp3'
    extract_audio(args.video, audio_file)

    frames_dir = dir_name + '/frames'
    os.makedirs(frames_dir)
    extract_frames(args.video, frames_dir)
    frames_count = len(glob(frames_dir + '/*'))
    audio_analyze = analyze(audio_file, frames_count)
    process(frames_dir, audio_analyze, args.size, neural=args.neural, colorize=args.colorize, brightify=args.brightify)
    construct_video(frames_dir, audio_file, get_fps(args.video), args.output)
    if not args.no_clean:
        rmtree(dir_name)


if __name__ == '__main__':
    main_arg_parser = argparse.ArgumentParser()
    main_arg_parser.add_argument("--video", "-v", type=str, required=True, help='Path to video file')
    main_arg_parser.add_argument("--neural", "-n", type=str, default=False,
                                 help='Path to neural models collection(def: False)')
    main_arg_parser.add_argument("--colorize", "-cl", action="store_true", help='Use colorization')
    main_arg_parser.add_argument("--brightify", "-br", action="store_true", help='Use brightness')
    main_arg_parser.add_argument("--size", "-s", type=int, default=1024, help='Result video resolution')
    main_arg_parser.add_argument("--output", "-o", type=str, required=True, help='Path to output file')
    main_arg_parser.add_argument("--no-clean", "-nc", action="store_true", help='Store .TEMP data')

    args = main_arg_parser.parse_args()
    main(args)
