import argparse
import os
from glob import glob

import ffmpy
import uuid
from style.stylish import process
import subprocess

from utils import get_fps, extract_frames, extract_audio, construct_video

AUDIO_DUR_CMD = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s'


def main(args):
    uid = uuid.uuid1()
    dir_name = './.TEMP-' + str(uid)
    os.makedirs(dir_name)

    audio_file = dir_name + '/audio.mp3'
    extract_audio(args.video, audio_file)

    frames_dir = dir_name + '/frames'
    os.makedirs(frames_dir)
    extract_frames(args.video, frames_dir)

    process(frames_dir, None, None)

    construct_video(frames_dir, audio_file, get_fps(args.video), args.output)


if __name__ == '__main__':
    main_arg_parser = argparse.ArgumentParser()
    main_arg_parser.add_argument("--video", "-v", type=str, required=True, help='Path to video file')
    main_arg_parser.add_argument("--model", "-m", type=str, required=True, help='Path to model file')
    main_arg_parser.add_argument("--size", "-s", type=int, default=1024, help='Result video resolution')
    main_arg_parser.add_argument("--output", "-o", type=str, required=True, help='Path to output file')

    args = main_arg_parser.parse_args()
    main(args)