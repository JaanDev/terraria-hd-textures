# Written by Jaan
# 06.01.2022

import glob
import ntpath
import sys

import cv2
from PIL import Image


def downscale_image(input_filename, output_filename):
    img = cv2.imread(input_filename, cv2.IMREAD_UNCHANGED)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

    if img.shape[1] == 1 or img.shape[0] == 1:
        return

    res = cv2.resize(img, dsize=(int(img.shape[1] / 2), int(img.shape[0] / 2)), interpolation=cv2.INTER_NEAREST)

    im = Image.fromarray(res)
    im.save(output_filename)


def downscale_images(input_dir, output_dir):
    for input_filename in glob.glob(f'{input_dir}/*.png'):
        output_filename = f'{output_dir}/{ntpath.basename(input_filename)}'

        try:
            downscale_image(input_filename=input_filename, output_filename=output_filename)
        except:
            print(f'Error processing file: "{output_filename}"')


if len(sys.argv) < 3:
    print("Usage: python %s input_dir output_dir" % (sys.argv[0],))
    print(
        "Downscale all *.png images in input_dir and saves the result in output_dir (with the same name). Not recursive.")
else:
    downscale_images(sys.argv[1], sys.argv[2])
