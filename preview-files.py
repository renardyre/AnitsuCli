#!/usr/bin/env python3

import json
import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)
IMG_LIST = os.path.join(SCRIPT_PATH, ".img_list")

def main():
    arg = sys.argv[1:]
    choose = arg[0].split('\t')
    index = choose[0]
    tree = choose[1]
    if index == "..": return

    try: image = arg[1].strip()
    except: image = ""

    if image:
        print('\n'*18)
        img = os.path.join(SCRIPT_PATH, 'Imgs', f'{index}.jpg')
        if os.path.exists(img):
            with open(IMG_LIST, 'w') as fp:
                fp.write(img)

    print('\n')
    tree = tree.replace('\'', '\"')
    tree = json.loads(tree)

    dirs = tree['Dirs']
    files = tree['Files']

    if len(dirs) > 0:
        print("\033[96m{}\033[0m".format('\n'.join([f" {i}" for i in dirs])))

    if len(files) > 0:
        for file in files:
            print("{} \033[94m{}\033[0m".format(fsize(file['Size']), file['Title']))

def fsize(size):
    size = int(size)
    units = ["KB", "MB", "GB", "TB", "PB"]
    fsize = f"{size} B"
    for i in units:
        if size < 1000:
            break
        size /= 1000
        fsize = f"{size:7.2f} {i}"
    return fsize


if __name__ == "__main__":
    main()
