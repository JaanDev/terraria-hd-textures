# Original by sullerandras
# Rewritten by Jaan#2897
# Edited and much helped by Vladimir.Ogre

import glob
import os
import shutil
import zipfile
from datetime import datetime
from subprocess import DEVNULL as no_stdout
from subprocess import run as run_command

SOURCE_XNB_FOLDER = 'source/Content/Images'
EXTRACTED_FOLDER = 'extracted'
DOWNSCALED_FOLDER = 'downscaled'
MAGNIFIED_FOLDER = 'magnified'
REFILLED_FOLDER = 'refilled'
RELEASE_FOLDER = 'release'
TEXTURE_PACK_FOLDER = 'texture-pack'


def prep_folders(path):
    flds = []
    for root, subdirs, files in os.walk(path):
        flds.append(root.replace(path, ''))
    return flds


def strfdelta(tdelta, fmt):
    d = {'days': tdelta.days}
    d['hours'], rem = divmod(tdelta.seconds, 3600)
    d['minutes'], d['seconds'] = divmod(rem, 60)
    return fmt.format(**d)


def extractPngsFromTerraria(input_, output):
    print(f'\n\nCalling TExtract {input_} => {output}')

    run_command(['java', '-jar', './tools/TExtract1.6.0.jar', '--outputDirectory', output + '.temp', input_],
                stdout=no_stdout)
    shutil.move(output + '.temp/Images', output)
    shutil.rmtree(output + '.temp', ignore_errors=True)


def downscalePngs(input_, output):
    FOLDERS = prep_folders(input_)

    print(f'\n\nDownscaling images {input_} => {output}')

    for folder in FOLDERS:
        os.makedirs(output + folder, exist_ok=True)

        run_command([shutil.which('python'), './tools/downscale.py', input_ + folder, output + folder])


def magnifyPngs(input_, output):
    FOLDERS = prep_folders(input_)

    print(f'\n\nMagnifying images {input_} => {output}')
    temp = f'{output}.temp'

    shutil.copytree(input_, temp, dirs_exist_ok=True)
    shutil.rmtree(f'{temp}/items-wrap', ignore_errors=True)
    os.makedirs(f'{temp}/items-wrap', exist_ok=True)

    for f in glob.glob(f'{temp}/Item_*.png'):
        shutil.move(f, temp + '/items-wrap')

    for folder in FOLDERS:
        os.makedirs(output + folder, exist_ok=True)

        for f in os.listdir(input_ + folder):
            if os.path.isfile(os.path.join(input_ + folder, f)):
                # run_command(['./tools/ImageResizer-r133.exe', '/load', os.path.join(input_ + folder, f), '/resize', 'auto', 'XBR 4x', '/save', os.path.join(output + folder, f)], stdout=no_stdout) doesnt work?? not sure
                run_command(['./tools/image_filter.exe', 'XBRz', temp + folder, output + folder], stdout=no_stdout)

    for f in os.listdir(temp + '/items-wrap'):
        if os.path.isfile(os.path.join(temp + '/items-wrap', f)):
            # run_command(['./tools/ImageResizer-r133.exe', '/load', os.path.join(temp + "/items-wrap", f), '/resize', 'auto', 'XBR 4x(vbounds=wrap,hbounds=wrap)', '/save', os.path.join(output, f)], stdout=no_stdout)
            run_command(['./tools/image_filter.exe', 'XBR', '-wrap', temp + '/items-wrap', output], stdout=no_stdout)


def refillMissingPixels(original_folder, input_, output):
    FOLDERS = prep_folders(input_)

    print(f'\n\nRefilling missing pixels in Walls and Tiles {input_} => {output}')

    shutil.copytree(input_, output, dirs_exist_ok=True)

    for folder in FOLDERS:
        os.makedirs(output + folder, exist_ok=True)
        run_command(
            [shutil.which('python'), './tools/refill_missing_pixels.py', original_folder + folder, input_ + folder,
             output + folder])


def zipfolder(zipname, target_dir):
    zipobj = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])


def createTexturePack(major_version, minor_version, terraria_version, input_, temp):
    version = f'v{major_version}.{minor_version}-{terraria_version}'
    out_file = f'HDTexturePack-{version}.zip'

    print(f'\n\nCreating zip file {out_file} with all textures')

    os.makedirs(f'{temp}/Content/Images', exist_ok=True)

    if os.path.exists(out_file):
        os.remove(out_file)

    shutil.copytree(input_, f'{temp}/Content/Images/', dirs_exist_ok=True)

    with open(f'{temp}/pack.json', 'w') as f:
        f.write('{'
                f'\n    "Name": "HD Textures {version}",'
                '\n    "Author": "Andras Suller & Jaan",'
                f'\n    "Description": "HD Textures {version}",'
                '\n    "Version": {'
                f'\n        "major": {major_version},'
                f'\n        "minor": {minor_version}'
                '\n    }'
                '\n}')

    zipfolder(out_file, temp)


# Main
if __name__ == '__main__':
    time_start_all = datetime.now()

    print('Starting...')

    # extractPngsFromTerraria(SOURCE_XNB_FOLDER, EXTRACTED_FOLDER)
    # downscalePngs(EXTRACTED_FOLDER, DOWNSCALED_FOLDER)
    magnifyPngs(DOWNSCALED_FOLDER, MAGNIFIED_FOLDER)
    # refillMissingPixels(EXTRACTED_FOLDER, MAGNIFIED_FOLDER, REFILLED_FOLDER)
    # createTexturePack(1, 0, '1.4.3.2', REFILLED_FOLDER, TEXTURE_PACK_FOLDER)

    time_end_all = datetime.now()

    print('\nFinished in: ' + strfdelta(time_end_all - time_start_all, '{hours}:{minutes}:{seconds}'))
