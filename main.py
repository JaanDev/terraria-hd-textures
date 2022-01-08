# Written by Jaan
# 06.01.2022
# All scripts that don't include "Written by Jaan" are not written by me.

import os
import PIL
from PIL import Image
import glob
import zipfile
import shutil
from datetime import datetime

SOURCE_XNB_FOLDER=r'ASSETS\Content\Images'
EXTRACTED_FOLDER='extracted'
DOWNSCALED_FOLDER='downscaled'
NO_SEPARATORS_FOLDER='no_seps'
MAGNIFIED_FOLDER='magnified'
REFILLED_FOLDER='refilled'
RELEASE_FOLDER='release'
TEXTURE_PACK_FOLDER='texture-pack'

def prep_folders(path):
    flds = []
    for root, subdirs, files in os.walk(path):
        flds.append('"' + root.replace(path, "").replace("\\", "/") + '",')

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

def extractPngsFromTerraria(input, output):
    print(f"\n\nCalling TExtract {input} => {output}")
    
    os.system(f'java -jar "tools/TExtract 1.6.0.jar" --outputDirectory {output}.temp {input}')
    os.system(f'move {output}.temp/Images {output}')
    shutil.rmtree(f'{output}.temp', ignore_errors=True)
    
def downscalePngs(input, output):
    FOLDERS = prep_folders(input)
    
    print(f"\n\nDownscaling images {input} => {output}")
    
    for folder in FOLDERS:
        print(f'Downscaling folder: "{input}{folder}"')
        os.makedirs(f"{output}{folder}", exist_ok=True)
        
        os.system(f'python ./tools/downscale.py "{input}{folder}" "{output}{folder}"')
        
def removeSeparators(input, output):
    FOLDERS = prep_folders(input)

    print(f"\n\nRemoving separators {input} => {output}")
    
    for folder in FOLDERS:
        os.makedirs(f"{output}{folder}", exist_ok=True)
        os.system(f'python .\\tools\\remove_separators.py "{input}{folder}" "{output}{folder}"')
        
def magnifyPngs(input, output, blend=True):
    FOLDERS = prep_folders(input)
    
    print(f"\n\nMagnifying images {input} => {output}")
    temp = f"{output}.temp"
    
    shutil.copytree(input, temp, dirs_exist_ok=True) 
    os.makedirs(f'{temp}/items-wrap', exist_ok=True)
    
    for f in glob.glob(f"{temp}/Item_*.png"):
        os.system(f'move "{f}" "{temp}/items-wrap"')
        print(f'move "{f}" "{temp}/items-wrap"')
        
    for folder in FOLDERS:
        print(f'Magnifying in folder: "{input}{folder}"')
        os.makedirs(f'{output}{folder}', exist_ok=True)
        
        if blend:
            os.system(f'.\\tools\\image_filter.exe "XBRz" "{temp}{folder}" "{output}{folder}"')
        else:
            os.system(f'.\\tools\\image_filter.exe "XBR-NoBlend" "{temp}{folder}" "{output}{folder}"')
    
    print('Magnifying items...')
    if blend:
        os.system(f'.\\tools\\image_filter.exe "XBR" -wrap "{temp}/items-wrap" "{output}"')
    else:
        os.system(f'.\\tools\\image_filter.exe "XBR-NoBlend" -wrap "{temp}/items-wrap" "{output}"')
        
def refillMissingPixels(original_folder, input, output):
    FOLDERS = prep_folders(input)
    
    print(f"\n\nRefilling missing pixels in Walls and Tiles {input} => {output}")
    
    shutil.copytree(input, output, dirs_exist_ok=True) 
    
    for folder in FOLDERS:
        print(f'Refilling in folder: "{input}{folder}"')
        os.makedirs(f'{output}{folder}', exist_ok=True)
        os.system(f'python .\\tools\\refill_missing_pixels.py {original_folder}{folder} {input}{folder} {output}{folder}')
        
def zipfolder(zipname, target_dir):            
    zipobj = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])
        
def createTexturePack(major_version, minor_version, terraria_version, input, temp):
    version = f"v{major_version}.{minor_version}-{terraria_version}"
    out_file = f"HDTexturePack-{version}.zip"
    
    print(f"\n\nCreating zip file {out_file} with all textures")
    
    os.makedirs(f'{temp}/Content/Images', exist_ok=True)
    
    if os.path.exists(out_file):
        os.remove(out_file)
        
    shutil.copytree(input, f"{temp}/Content/Images/", dirs_exist_ok=True) 
    
    with open(f'{temp}/pack.json', "w") as f:
        f.write('{'
f'\n    "Name": "HD Textures {version}",'
'\n    "Author": "Andras Suller & Jaan",'
f'\n    "Description": "HD Textures {version}",'
'\n    "Version": {'
f'\n        "major": {major_version},'
f'\n        "minor": {minor_version}'
'\n    }'
'\n}')
    
    with open(f'{temp}/README.txt', "w") as f:
        f.write(f'Enhanced version of the textures of Terraria {terraria_version}'
        
f'\n\nCreated by Andras Suller, "pythoned" and fixed by Jaan, texturepack {version}.'
'\nFor more information visit: http://forums.terraria.org/index.php?threads/enhanced-version-of-the-textures-of-terraria-1-3-0-8.39115/')

    zipfolder(out_file, temp)
    
# Main
time_start_all = datetime.now()

print("Starting...")

extractPngsFromTerraria(SOURCE_XNB_FOLDER, EXTRACTED_FOLDER)
downscalePngs(EXTRACTED_FOLDER, DOWNSCALED_FOLDER)
removeSeparators(DOWNSCALED_FOLDER, NO_SEPARATORS_FOLDER)
magnifyPngs(NO_SEPARATORS_FOLDER, MAGNIFIED_FOLDER, True)
refillMissingPixels(EXTRACTED_FOLDER, MAGNIFIED_FOLDER, REFILLED_FOLDER)
createTexturePack(1, 0, '1.4.3.2', REFILLED_FOLDER, TEXTURE_PACK_FOLDER)

time_end_all = datetime.now()

print("\nFinished in: " + strfdelta(time_end_all - time_start_all, "{hours}:{minutes}:{seconds}"))