#!/usr/bin/env python3

import json
import sys
import os
import re


script_path = os.path.dirname(__file__)
arg = sys.argv
with open(arg[1], 'r') as f:
    tituloLimpo = f.read().strip()
    index = re.sub(r'[/:&\(\)\-\"\”\“ ]',"",tituloLimpo.strip())
os.system("pkill feh")

if index == "..": exit()

#with open(f'{script_path}/Anitsu.json', 'r') as file:
#	db = json.load(file)

#value = [ i for i in db.values() if i["TituloLimpo"] == tituloLimpo][0]
#imgs = dict([ (value['TituloLimpo'].replace(" ", "").replace("/", ""), value['Imagem']) for value in db.values() ])
#if index not in imgs.keys(): exit()
#os.system(f"feh {imgs[index]} --scale-down --auto-zoom -q -x --image-bg black -g 444x653 --class FloatingFeh > /dev/null 2>&1 &")

os.system(f"feh {script_path}/Imgs/{index}.jpg --scale-down --auto-zoom -q -x --image-bg black -g 444x653 --class FloatingFeh > /dev/null 2>&1 &")
#print("\n".join(value["Tags"]))
#print(f"{value['Titulo']}\n\n{'\n'.join(value['Tags']) if 'Tags' in value.keys() else ''}")

