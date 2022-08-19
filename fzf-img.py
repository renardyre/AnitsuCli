#!/usr/bin/env python3

import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)

def main():
    arg = sys.argv
    with open(arg[1], 'r') as f:
        clean_title = f.read().strip()
        index = re.sub(r'[/:&\(\)\-\"\”\“ ]',"",clean_title.strip())
    os.system("pkill feh")

    if index == "..": exit()

    os.system(f"feh {SCRIPT_PATH}/Imgs/{index}.jpg \
        --scale-down --auto-zoom -q -x --image-bg black -g 444x653 --class FloatingFeh > /dev/null 2>&1 &")

if __name__ == "__main__":
    main()