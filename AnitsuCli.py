#!/usr/bin/env python3

from pyfzf.pyfzf import FzfPrompt
from dotenv import load_dotenv
from shutil import which
from time import sleep
import pyperclip
import requests
import argparse
import json
import os
import re

parser = argparse.ArgumentParser(description="Lista e reproduz animes disponíveis na Anitsu")
parser.add_argument('-i', '--image', action='store_true', help='Habilita capa dos animes')
parser.add_argument('-p', '--player', default='mpv', type=str, choices=['mpv', 'syncplay'], help='Seleciona o player a ser utilizado. Padrão: mpv')
parser.add_argument('-l', '--links', action='store_true', help='Em vez de reproduzir, retorna os links dos arquivos selecionados')
parser.add_argument('-m', '--multi', action='store_true', help='Habilita seleção multipla de episódios')
parser.add_argument('-o', '--one', action='store_true', help='Reproduz apenas um episódio')
parser.add_argument('-t', '--tags', action='store_true', help='Seleciona tags')
parser.add_argument('-u', '--update', action='store_true', help='Atualiza a base de dados')

SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(SCRIPT_PATH, "Anitsu.json")
FZF_IMG = os.path.join(SCRIPT_PATH, ".fzf_img.jpg")
FZF_IMG_LIST = os.path.join(SCRIPT_PATH, ".img_list")
args = parser.parse_args()

player = args.player
showImages = args.image
returnLinks = args.links
multiSelection = args.multi
oneEpisode = args.one
selectTags = args.tags
update = args.update

if update or not os.path.exists(DB_PATH):
    commands = ['clear', 'tput civis', f'python3 {SCRIPT_PATH}/PostsAnitsu.py', f'python3 {SCRIPT_PATH}/WebdavGetTree.py', 'tput cnorm']
    for c in commands:
        os.system(c)
    exit()

if returnLinks:
    load_dotenv()
    ARIA_URL = os.getenv('ARIA_URL')
    ARIA_TOKEN = os.getenv('ARIA_TOKEN')

fzf_args_img = '-i -e --delimiter="\t" --with-nth=-1 --reverse --cycle --height 100% --preview-window="right,60%,border-left,wrap" --preview="' + SCRIPT_PATH + '/fzf-img.py {}"'
fzf_args = '-i -e --delimiter="\t" --with-nth=-1 --reverse --cycle --height 100%'

with open(DB_PATH, 'r') as file:
    database = json.load(file)

fzf = FzfPrompt()

if selectTags:
    allTags = [ j for i in database.values() if "Tags" in i.keys() for j in i["Tags"]]
    uniqueTags = list(set(sorted(allTags)))
    uniqueTags.sort()
    uniqueTags = [f"{i} ({allTags.count(i)})" for i in uniqueTags]
    tags = fzf.prompt(uniqueTags+['..'], fzf_args + " -m")
    if '..' in tags: exit()
    tags = [ ' '.join(i.split(' ')[:-1]) for i in tags ]


def start_feh():
    os.system(f'convert xc:black -size 1x1 {FZF_IMG}')
    with open(FZF_IMG_LIST, 'w') as fp:
        fp.write(FZF_IMG)
    os.system(f'feh -f {FZF_IMG_LIST} --scale-down --reload 0.1 --auto-zoom -q -x --image-bg black --class FloatingFeh >/dev/null 2>&1 &')


def choose_anime():
    keys = sorted([ int(i) for i in database.keys()], reverse=True)
    if selectTags: 
        titulosAnimes = [  f"{str(i)}\t{database[str(i)]['Description']}\t{clean_title(database[str(i)]['Title'])}" \
        for i in keys if "Tags" in database[str(i)] and set(tags) & set(database[str(i)]["Tags"])]
    else:
        titulosAnimes = [  f"{str(i)}\t{database[str(i)]['Description']}\t{clean_title(database[str(i)]['Title'])}" \
        for i in keys ]
    
    os.system('clear')

    try:
        if showImages:
            start_feh()
            escolha = fzf.prompt(titulosAnimes+['..\t..'], fzf_args_img)[0]
        else:
            escolha = fzf.prompt(titulosAnimes+['..\t..'], fzf_args)[0]
    finally:
        try:
            os.system("pkill feh")
        except:
            pass
        if escolha == '..\t..':
            exit(0)

    index = escolha.split('\t')[0]
    return (database[index], index)

def choose_eps(anime):
    choosed = False
    if "Tree" not in anime.keys(): return
    file_tree = anime["Tree"]
    previous = []

    while not choosed:

        dirs = [ f" {dir}" for dir in file_tree['Dirs'].keys() ]
        files = [ file['Title'] for file in file_tree['Files'] ]

        if multiSelection:
            choose = fzf.prompt(dirs+files+['..'], fzf_args + " -m --bind ctrl-a:toggle-all+last+toggle+first")
        else:	
            choose = fzf.prompt(dirs+files+['..'], fzf_args)

        if choose[0] in dirs:
            previous.append(file_tree.copy())
            file_tree = file_tree["Dirs"][choose[0][2:]]
    
        elif choose[0] in files:
            if multiSelection:
                episodes = []
                for ep in choose:
                    ep_num = files.index(ep)
                    episodes.append(file_tree["Files"][ep_num])
                choosed = True
            else:
                if oneEpisode:
                    escolha_num = files.index(choose[0])
                    episodes = [file_tree["Files"][escolha_num]]
                    choosed = True	
                else:
                    escolha_num = files.index(choose[0])
                    episodes = file_tree["Files"][escolha_num:]
                    choosed = True
    
        elif choose[0] == "..":
            if len(previous) == 0:
                return
            file_tree = previous.pop()

    return episodes


def watch(episodes):
    if returnLinks:
        links = "\n".join([ f"https://{i['Link']}" for i in episodes ])
        try: pyperclip.copy(links)
        except: pass
        try:
            for i in episodes:
                payload = {'jsonrpc':'2.0', 'id':'0', 'method':'aria2.addUri', 'params':[f'token:{ARIA_TOKEN}', [f"https://{i['Link']}"]]}
                r = requests.post(ARIA_URL, data=json.dumps(payload))
        except: pass
        print(links)
        exit()

    if player == "syncplay":
        with open(f'{SCRIPT_PATH}/.playlist.txt', 'w') as pl:
            pl.write("\n".join([ f'https://{i["Link"]}' for i in episodes ]))
        os.system(f"syncplay --no-store --load-playlist-from-file '{SCRIPT_PATH}/.playlist.txt'")
    else:
        with open(f'{SCRIPT_PATH}/.playlist.m3u', 'w') as pl:
            pl.write('#EXTM3U\n')
            for ep in episodes:
                pl.write(f"#EXTINF:0, {ep['Title']}\nhttps://{ep['Link']}\n")
        if which("mpv"):
            os.system(f"mpv --fs --playlist={SCRIPT_PATH}/.playlist.m3u")
        else:
            print("Mpv not installed, please install to reproduce the files!")
            exit()

def main():
    while True:
        anime, image = choose_anime()
        title = clean_title(anime["Title"])
        if showImages:
            os.system('pkill feh')
        episodes = choose_eps(anime)
        if episodes:
            if not returnLinks and which("dunstify"):
                os.system(f"dunstify 'AnitsuCli: Started playing' '{title}' -I {SCRIPT_PATH}/Imgs/{image}.jpg")
            watch(episodes)

def clean_title(str: str):
    return re.search(r'^.*?(?=(?: DUAL| Blu\-[Rr]ay| \[|$))', str).group()

if __name__ == "__main__":
    main()
