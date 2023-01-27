#!/usr/bin/env python3

import json
import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)
FEH_IMG_LIST = os.path.join(SCRIPT_PATH, ".img_list")

def main():
    arg = sys.argv[1:][0].split('\t')
    index = arg[0]
    choose = arg[1]

    img = os.path.join(SCRIPT_PATH, 'Imgs', f'{index}.jpg')
    if os.path.exists(img):
        with open(FEH_IMG_LIST, 'w') as fp:
            fp.write(img)

    tree = choose.replace('\'', '\"')
    tree = json.loads(tree)
    print('\n'*20)

    dirs = tree['Dirs']
    files = tree['Files']

    if len(dirs) > 0:
        print("\033[96m{}\033[0m".format('\n'.join([f" {i}" for i in dirs])))

    if len(files) > 0:
        print("{}".format('\n'.join([i['Title'] for i in files])))

if __name__ == "__main__":
    try:
        main()
    except:
        pass
