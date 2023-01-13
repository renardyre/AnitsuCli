#!/usr/bin/env python3

from pyfzf.pyfzf import FzfPrompt
from dotenv import load_dotenv
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

    if which('feh'):
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

    while not choosed:

        dirs = [ f" {dir}" for dir in file_tree['Dirs'].keys() ]
        files = [ file['Title'] for file in file_tree['Files'] ]

        choose = fzf.prompt(dirs+files+['..'], fzf_args + " -m --bind='ctrl-a:toggle-all+last+toggle+first'")

        if choose[0] in dirs:
            previous.append(file_tree.copy())
            file_tree = file_tree["Dirs"][choose[0][2:]]
    
        elif choose[0] in files:
            episodes = []
            for ep in choose:
                ep_num = files.index(ep)
                episodes.append(file_tree["Files"][ep_num])
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
        episodes = choose_eps(anime)
        if episodes:
            if not returnLinks and which("dunstify"):
                os.system(f"dunstify 'AnitsuCli: Started playing' '{title}' -I {SCRIPT_PATH}/Imgs/{image}.jpg")
            watch(episodes)

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
    parser.add_argument('-v', '--version', action='version', version='AnitsuCli (v0.1.0)', help="Mostra a versão do programa")
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Mostra esta mensagem de ajuda')
    
    SCRIPT_PATH = os.path.dirname(__file__)
    DB_PATH = os.path.join(SCRIPT_PATH, "Anitsu.json")
    args = parser.parse_args()
    
    player = args.player
    returnLinks = args.links
    selectTags = args.tags
    update = args.update
    
    if not which('fzf'):
        print("Fzf not installed, please install to navigate!")
    
    if returnLinks:
        load_dotenv()
        ARIA_URL = os.getenv('ARIA_URL')
        ARIA_TOKEN = os.getenv('ARIA_TOKEN')
    
    bindings = [
            f"ctrl-p:execute-silent({SCRIPT_PATH}/HandleFeh.py start)+change-preview({SCRIPT_PATH}/preview-img.py {{}})",
            f"ctrl-f:execute-silent({SCRIPT_PATH}/HandleFeh.py stop)+change-preview({SCRIPT_PATH}/preview-files.py {{2}})",
            "ctrl-w:toggle-preview-wrap"]
    
    fzf_args_preview = f' --preview-window="right,60%,border-left,wrap" --preview="" --bind="{",".join(bindings)}"'
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

    if update or not os.path.exists(DB_PATH):
        clear_terminal()
        asyncio.run(PostsAnitsu.main())
        asyncio.run(WebdavGetTree.main())
        exit()
    main()
