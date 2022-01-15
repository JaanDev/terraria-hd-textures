# Written by Jaan
# Concept by sullerandras
# 07.01.2022

import glob
import ntpath
import os
import sys

import cv2
from PIL import Image


def refill(output_name, input_name, original_name):
    # LOGIC:
    # 1. Get input and orig sprites
    # 2. Overlay input img on original one
    # 3. Profit lol

    input_img = Image.open(input_name).convert('RGBA')
    orig_img = Image.open(original_name).convert('RGBA')

    Image.alpha_composite(orig_img, input_img).save(output_name)


def refill_in_folder(original_dir, input_dir, output_dir):
    for item in glob.glob(f'{input_dir}/Wall_*.png'):
        if "Wall_Outline" in item:
            continue

        try:
            refill(os.path.join(output_dir, os.path.basename(item)), item,
                   os.path.join(original_dir, os.path.basename(item)))
        except:
            print("Error during refilling for file: " + item)

    for item in glob.glob(f'{input_dir}/Tiles_*.png'):
        try:
            refill(os.path.join(output_dir, os.path.basename(item)), item,
                   os.path.join(original_dir, os.path.basename(item)))
        except:
            print("Error during refilling for file: " + item)


if len(sys.argv) < 3:
    print(f"Usage: python {sys.argv[0]} original_dir input_dir output_dir")
    print(
        "Refilles pixels that were lost during magnification for walls and tiles in input_dir and saves the result in output_dir (with the same name). Not recursive.")
else:
    refill_in_folder(sys.argv[1], sys.argv[2], sys.argv[3])
