#!/usr/bin/env python3

import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)

def main():
    arg = sys.argv
    with open(arg[1], 'r') as f:
        choose = f.read().strip().split('\t')
    os.system("pkill feh")

    index = choose[0]
    if index == "..": return

    print('\n'*20)
    text = choose[1].replace('NeLi', '\n')
    print(re.sub(r'(.*)(?:\:)' , r'\033[4m\033[1m\1:\033[0m', text))

    os.system(f"feh \'{SCRIPT_PATH}/Imgs/{index}.jpg\' \
        --scale-down --auto-zoom -q -x --image-bg black --class FloatingFeh > /dev/null 2>&1 &")

if __name__ == "__main__":
    main()
