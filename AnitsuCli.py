#!/usr/bin/env python3

from pyfzf.pyfzf import FzfPrompt
from dotenv import load_dotenv
from threading import Thread
from shutil import which
from time import sleep
import subprocess as sp
import WebdavGetTree
import PostsAnitsu
import HandleFeh
import pyperclip
import requests
import argparse
import asyncio
import json
import os
import re


def choose_anime():
    keys = sorted([ int(i) for i in database.keys()], reverse=True)
    if selectTags: 
        titulosAnimes = [
                f"{str(i)}\t{{'Dirs': {list(database[str(i)]['Tree']['Dirs'].keys())}, 'Files': {list(database[str(i)]['Tree']['Files'])}}}\t{database[str(i)]['Description']}\t{clean_title(database[str(i)]['Title'])}" for i in keys if "Tags" in database[str(i)] and set(tags) & set(database[str(i)]["Tags"])
        ]
    else:
        titulosAnimes = [
                f"{str(i)}\t{{'Dirs': {list(database[str(i)]['Tree']['Dirs'].keys())}, 'Files': {list(database[str(i)]['Tree']['Files'])}}}\t{database[str(i)]['Description']}\t{clean_title(database[str(i)]['Title'])}" for i in keys
        ]
    
    clear_terminal()

    escolha = fzf.prompt(titulosAnimes+['..\t..'], fzf_args + fzf_args_preview)[0]

    if preview == "ueberzug":
        with open(img_list, 'w') as fp:
            fp.write('kill')
    elif preview == "feh":
        HandleFeh.stop_feh()

    if escolha == '..\t..':
        exit(0)

    index = escolha.split('\t')[0]
    return (database[index], index)

def choose_eps(anime):
    choosed = False
    if "Tree" not in anime.keys(): return
    file_tree = anime["Tree"]
    previous = []
    path = [anime["Title"]]

    while not choosed:

        dirs = [ f" {dir}" for dir in file_tree['Dirs'].keys() ]
        files = [ file['Title'] for file in file_tree['Files'] ]

        choose = fzf.prompt(dirs+files+['..'], fzf_args + " -m --bind='ctrl-a:toggle-all+last+toggle+first'")

        if choose[0] in dirs:
            dir = choose[0][2:]
            previous.append(file_tree.copy())
            path.append(dir)
            file_tree = file_tree["Dirs"][dir]
    
        elif choose[0] in files:
            episodes = []
            for ep in choose:
                ep_num = files.index(ep)
                episodes.append(file_tree["Files"][ep_num])
            choosed = True
    
        elif choose[0] == "..":
            if len(previous) == 0:
                return ('','')
            file_tree = previous.pop()
            path.pop()

    return episodes, "/".join(path)


def watch(episodes, path):
    if returnLinks:
        links = "\n".join([ f"https://{i['Link']}" for i in episodes ])
        try: pyperclip.copy(links)
        except: pass
        try:
            for i in episodes:
                if ARIA_DIR:
                    payload = {'jsonrpc':'2.0', 'id':'0', 'method':'aria2.addUri', 'params':[f'token:{ARIA_TOKEN}', [f"https://{i['Link']}"], {'dir': f"{ARIA_DIR}/{path}"}]}
                else:
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
        if preview == "ueberzug":
            t = Thread(target=preview_ueberzug.main)
            t.start()
        elif preview == "feh":
            HandleFeh.start_feh()

        anime, image = choose_anime()
        title = clean_title(anime["Title"])
        episodes, path = choose_eps(anime)
        if episodes:
            if not returnLinks and which("dunstify"):
                os.system(f"dunstify 'AnitsuCli: Started playing' '{title}' -I {SCRIPT_PATH}/Imgs/{image}.jpg")
            watch(episodes, path)

def clean_title(str: str):
    return re.search(r'^.*?(?=(?: DUAL| Blu\-[Rr]ay| \[|$))', str).group()

def clear_terminal():
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lista e reproduz animes disponíveis na Anitsu", add_help=False)
    parser.add_argument('-p', '--player', default='mpv', type=str, choices=['mpv', 'syncplay'], help='Seleciona o player a ser utilizado. Padrão: mpv')
    parser.add_argument('-l', '--links', action='store_true', help='Em vez de reproduzir, retorna os links dos arquivos selecionados')
    parser.add_argument('-t', '--tags', action='store_true', help='Seleciona tags')
    parser.add_argument('-u', '--update', action='store_true', help='Atualiza a base de dados')
    parser.add_argument('-v', '--version', action='version', version='AnitsuCli (v0.1.2)', help="Mostra a versão do programa")
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Mostra esta mensagem de ajuda')
    
    SCRIPT_PATH = os.path.dirname(__file__)
    DB_PATH = os.path.join(SCRIPT_PATH, "Anitsu.json")
    args = parser.parse_args()
    
    player = args.player
    returnLinks = args.links
    selectTags = args.tags
    update = args.update

    if update or not os.path.exists(DB_PATH):
        clear_terminal()
        asyncio.run(PostsAnitsu.main())
        asyncio.run(WebdavGetTree.main())
        exit()
   
    if not which('fzf'):
        print("Fzf not installed, please install to navigate!")
        exit()
    
    if returnLinks:
        load_dotenv()
        ARIA_URL = os.getenv('ARIA_URL')
        ARIA_TOKEN = os.getenv('ARIA_TOKEN')
        ARIA_DIR = os.getenv('ARIA_DIR')
    
    preview = "feh" if which("feh") else ""
    try:
        import preview_ueberzug
        preview = "ueberzug"
    except:
        pass

    if os.getenv('DISPLAY') and os.name != "nt" and preview != "":

        img_list = os.path.join(SCRIPT_PATH, '.img_list')
        try:
            os.remove(img_list)
        finally:
            if preview == "ueberzug":
                os.mkfifo(img_list)
            else:
                open(img_list, 'w').close()

        default_preview = f"{SCRIPT_PATH}/preview-img.py {{}} 'image'"
        bindings = [
                f"ctrl-p:change-preview({default_preview})",
                f"ctrl-f:change-preview({SCRIPT_PATH}/preview-files.py {{1..2}} 'image')",
                "ctrl-w:toggle-preview-wrap"]
    else:
        default_preview = ""
        bindings = [
                f"ctrl-p:change-preview({SCRIPT_PATH}/preview-img.py {{}})",
                f"ctrl-f:change-preview({SCRIPT_PATH}/preview-files.py {{1..2}})",
                "ctrl-w:toggle-preview-wrap"]

    fzf_args_preview = f' --preview-window="right,60%,border-left,wrap" --preview="{default_preview}" --bind="{",".join(bindings)}"'
    fzf_args = '-i -e --delimiter="\t" --with-nth=-1 --reverse --cycle --height 100%'
    
    with open(DB_PATH, 'r') as file:
        database = json.load(file)
    
    fzf = FzfPrompt()
    
    if selectTags:
        allTags = [ j for i in database.values() if "Tags" in i.keys() for j in i["Tags"]]
        uniqueTags = list(set(sorted(allTags)))
        uniqueTags.sort()
        uniqueTags = [f"{i} ({allTags.count(i)})" for i in uniqueTags]
        tags = fzf.prompt(uniqueTags+['..'], fzf_args + " -m --bind='ctrl-a:toggle-all+last+toggle+first'")
        if '..' in tags: exit()
        tags = [ ' '.join(i.split(' ')[:-1]) for i in tags ]

    main()
