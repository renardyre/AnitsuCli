#!/usr/bin/env python3

from shutil import which
import os
import sys
import signal
import subprocess as sp

SCRIPT_PATH = os.path.dirname(__file__)
FEH_IMG = os.path.join(SCRIPT_PATH, ".feh_img.jpg")
FEH_PID = os.path.join(SCRIPT_PATH, ".feh_pid")
IMG_LIST = os.path.join(SCRIPT_PATH, ".img_list")

def start_feh():
    with open(FEH_PID, 'r') as fp:
        pid = fp.read() 
    if pid != "stopped":
        return

    os.system(f'convert xc:black -size 1x1 {FEH_IMG}')
    with open(IMG_LIST, 'w') as fp:
        fp.write(FEH_IMG)

    command = ['feh', '-f', IMG_LIST, '--scale-down', '--reload', '0.1', '--auto-zoom', '-q', '-x', '--image-bg', 'black', '--class', 'FloatingFeh']
    pid = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE,).pid

    with open(FEH_PID, 'w') as fp:
        fp.write(str(pid))

def stop_feh():
    with open(FEH_PID, 'r+') as fp:
        pid = fp.read() 

        if pid != "stopped":
            fp.seek(0)
            fp.write("stopped")
            fp.truncate()
            try:
                os.kill(int(pid), signal.SIGTERM)
            except:
                pass

if __name__ == "__main__":
    if not which('feh'): exit(1)
    args = sys.argv
    if len(args) == 1:
        exit(0)
    elif args[1] == 'start':
        start_feh()
    elif args[1] == 'stop':
        stop_feh()
