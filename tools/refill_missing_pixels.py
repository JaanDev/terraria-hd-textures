# Written by Jaan
# Concept by sullerandras
# 07.01.2022

import os
import sys
from PIL import Image
import cv2
import glob
import ntpath

def refill(output_name, input_name, original_name):
    # LOGIC:
    # 1. Get input and orig sprites
    # 2. Overlay magnified img on original one
    # 3. Profit lol
    
    input_img = Image.open(input_name).convert('RGBA')
    orig_img = Image.open(original_name).convert('RGBA')
    
    #orig_img.paste(input_img, (0,0), input_img)
    Image.alpha_composite(orig_img, input_img).save(output_name)
    
    #orig_img.save(output_name)

def refill_in_folder(original_dir, input_dir, output_dir):
    for item in glob.glob(f'{input_dir}/Wall_*.png'):
        if "Wall_Outline" in item:
            continue
        
        # print(item)
        
        try:
            refill(f'{output_dir}/{ntpath.basename(item)}', item, f'{original_dir}/{ntpath.basename(item)}')
        except:
            print("Error during refilling for file: " + item)

if len(sys.argv) < 3:
    print("Usage: python %s original_dir input_dir output_dir" % (sys.argv[0],))
    print("Refilles pixels that were lost during magnification for walls and tiles in input_dir and saves the result in output_dir (with the same name). Not recursive.")
else:
    refill_in_folder(sys.argv[1], sys.argv[2], sys.argv[3])