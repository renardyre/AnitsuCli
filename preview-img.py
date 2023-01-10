#!/usr/bin/env python3

from shutil import which
import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)

def main():
    arg = sys.argv[1:]
    choose = arg[0].strip().split('\t')

    feh = which('feh')
    if which(feh):
        os.system("pkill feh")
        print('\n'*18)

    index = choose[0]
    if index == "..": return

    print('\n')
    text = choose[2].replace('NeLi', '\n')
    print(re.sub(r'(.*)(?:\:)' , r'\033[4m\033[1m\1:\033[0m', text))

    if feh:
        os.system(f"feh \'{SCRIPT_PATH}/Imgs/{index}.jpg\' \
            --scale-down --auto-zoom -q -x --image-bg black --class FloatingFeh > /dev/null 2>&1 &")

if __name__ == "__main__":
    main()
