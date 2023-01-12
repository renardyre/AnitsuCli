#!/usr/bin/env python3

from shutil import which, copy
from time import sleep
import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)
FEH_IMG_LIST = os.path.join(SCRIPT_PATH, ".img_list")

def main():
    arg = sys.argv[1:]
    choose = arg[0].strip().split('\t')
    index = choose[0]
    if index == "..": return

    if which('feh'):
        print('\n'*18)
        img = os.path.join(SCRIPT_PATH, 'Imgs', f'{index}.jpg')
        if os.path.exists(img): 
            with open(FEH_IMG_LIST, 'w') as fp:
                fp.write(img)

    print('\n')
    text = choose[2].replace('NeLi', '\n')
    print(re.sub(r'(.*)(?:\:)' , r'\033[4m\033[1m\1:\033[0m', text))

if __name__ == "__main__":
    main()
