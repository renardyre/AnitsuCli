#!/usr/bin/env python3

import json
import sys
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)

def main():
    arg = sys.argv[1:]
    choose = arg[0]

    tree = choose.replace('\'', '\"')
    tree = json.loads(tree)
    print('\n')

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
