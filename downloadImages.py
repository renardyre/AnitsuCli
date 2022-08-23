#!/usr/bin/env python3

import requests
import json
import os
import re


SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = f"{SCRIPT_PATH}/Anitsu.json"
T_COLUMNS = os.get_terminal_size().columns - 10

def main():
  with open(DB_PATH, 'r') as file:
    db = json.load(file)

  downloaded = os.listdir(f"{SCRIPT_PATH}/Imgs")
  imgs = dict(
    [ (clean_title(value['Title']), value['Image']) \
    for value in db.values() if f'{clean_title(value["Title"])}.jpg' not in downloaded])
  counter = 1

  if imgs:
    print(f"\nDownloading {len(imgs)} image(s)!\n")
    for index, value in imgs.items():
      r = requests.get(value)

      filename = f"{index}.{value.split('.')[-1]}"
      with open(f"{SCRIPT_PATH}/Imgs/{filename}", 'wb') as file:
        file.write(r.content)
 
      prop = counter * 100 // len(imgs)
      text = f" => {prop:3}% "
      remain = T_COLUMNS - len(text) - 4
      progress = "|" * (prop * remain // 100)
      blank = " " * (remain - len(progress))
      print(f"{text}[ {progress}{blank} ] ", end="\r")
      
      os.system(f"convert \'{SCRIPT_PATH}/Imgs/{filename}\' -resize 444x654 \'{SCRIPT_PATH}/Imgs/{index}.jpg\'")
      if ".jpg" not in filename:
        os.system(f"rm {SCRIPT_PATH}/Imgs/{filename}")

      if f"{index}-0.jpg" in os.listdir(f"{SCRIPT_PATH}/Imgs"):
        os.system(f"mv \'{SCRIPT_PATH}/Imgs/{index}-0.jpg\' \'{SCRIPT_PATH}/Imgs/{index}.jpg\'")    
      counter += 1

    os.chdir(f"{SCRIPT_PATH}/Imgs")
    if "-" in "".join(os.listdir()):
      os.system(f'ls | grep -P "\-" | xargs -d"\n" rm')
  
    print()
    os.chdir(SCRIPT_PATH)

def clean_title(str: str):
  clean_title = re.search(r'^.*?(?=(?: DUAL| Blu\-[Rr]ay| \[|$))', str).group()
  return re.sub(r'[/:&\(\)\-\"\”\“ ]',"",clean_title)

if __name__ == "__main__":
  main()