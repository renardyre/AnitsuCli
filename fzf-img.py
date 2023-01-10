#!/usr/bin/env python3

from shutil import which, copy
from time import sleep
import sys
import os
import re

FZF_IMG = '/tmp/Anitsu.jpg'
SCRIPT_PATH = os.path.dirname(__file__)

def main():
    arg = sys.argv[1:]
    choose = arg[0].strip().split('\t')
    index = choose[0]
    if index == "..": return

    if which('feh'):
        print('\n'*18)
        img = f'{SCRIPT_PATH}/Imgs/{index}.jpg'
        if os.path.exists(img): 
            sleep(0.3)
            copy(img, FZF_IMG)
            os.system(f'touch {FZF_IMG}')

    print('\n')
    text = choose[1].replace('NeLi', '\n')
    print(re.sub(r'(.*)(?:\:)' , r'\033[4m\033[1m\1:\033[0m', text))

if __name__ == "__main__":
    main()
