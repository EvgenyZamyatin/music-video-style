import subprocess
import numpy as np
import argparse
import os

import shutil


def main(args):
    params = {
        '--train-dir': './data/train2014',
        '--val-dir': './data/train2014',
        '--test-image': './data/images/ghc.jpg',
        '--test-size': '1024',
        '--checkpoint': '',
        '--style-image': args.style_image,
        '--train-iter': '100'
    }
    name = os.path.basename(args.style_image)[:-4]
    for i, sw in enumerate(np.linspace(args.start, args.end, args.n)):
        break
        params['--style-weight'] = str(sw)
        output = args.output + '/' + name + '/%d' % i
        params['--output-dir'] = output
        if i != 0:
            params['--model'] = args.output + '/%d' % (i-1) + '/model.h5'
        subprocess.call('python3 style/fast_neural_style/fast_neural_style.py train ' + ' '.join(' '.join(item) for item in params.items()),
                        shell=True)
    result_dir = './data/models/%s' % name

    os.makedirs(result_dir)
    for i in range(args.n):
        shutil.copy(args.output + '/' + name + '/%d' % i + '/model.h5', result_dir + '/%d.h5')


if __name__ == '__main__':
    main_arg_parser = argparse.ArgumentParser()
    main_arg_parser.add_argument("--style-image", type=str, required=True, help='Path to style image')
    main_arg_parser.add_argument("--output", type=str, required=True, help='Path to output dir')
    main_arg_parser.add_argument("--start", type=float, required=True, help='Start style weight')
    main_arg_parser.add_argument("--end", type=float, required=True, help='End style weight')
    main_arg_parser.add_argument("--n", type=int, required=True, help='Count')

    args = main_arg_parser.parse_args()
    main(args)
