#!/usr/bin/env python3

from pyfzf.pyfzf import FzfPrompt
import pyperclip
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


args = parser.parse_args()

player = args.player
showImages = args.image
returnLinks = args.links
multiSelection = args.multi
oneEpisode = args.one
selectTags = args.tags

script_path = os.path.dirname(__file__)
fzf_args_img = '-i --reverse --cycle --height 100% --preview-window 0% --preview="' + script_path + '/fzf-img.py {f}"'
fzf_args = '-i --reverse --cycle --height 100%'

with open(f'{script_path}/Anitsu.json', 'r') as file:
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

def choose_anime():

  keys = sorted([ int(i) for i in database.keys()], reverse=True)
  if selectTags: 
    db = [ database[str(i)] for i in keys if "Tags" in database[str(i)] and set(tags) & set(database[str(i)]["Tags"])]
  else:
    db = [ database[str(i)] for i in keys ]
  titulosAnimes = [ clean_title(i['Title']) for i in db ]
  os.system('clear')

  if showImages:
    escolha = fzf.prompt(titulosAnimes+['..'], fzf_args_img)[0]
  else:
    escolha = fzf.prompt(titulosAnimes+['..'], fzf_args)[0]

  if escolha == '..': exit(0)
  index = titulosAnimes.index(escolha)
  
  return db[int(index)]

def choose_eps(anime):
  escolheu = False
  if "Tree" not in anime.keys(): return
  FILES = anime["Tree"]
  anterior = []

  while not escolheu:

    diretorios = [ f"ﱮ {dir}" for dir in FILES['Dirs'].keys() ]
    arquivos = [ file['Title'] for file in FILES['Files'] ]

    if multiSelection:
      escolha = fzf.prompt(diretorios+arquivos+['..'], fzf_args + " -m")
    else:	
      escolha = fzf.prompt(diretorios+arquivos+['..'], fzf_args)


    if escolha[0] in diretorios:
      anterior.append(FILES.copy())
      FILES = FILES["Dirs"][escolha[0][2:]]
    
    elif escolha[0] in arquivos:
      if multiSelection:
        episodes = []
        for ep in escolha:
          ep_num = arquivos.index(ep)
          episodes.append(FILES["Files"][ep_num])
        escolheu = True
      else:
        if oneEpisode:
          escolha_num = arquivos.index(escolha[0])
          episodes = [FILES["Files"][escolha_num]]
          escolheu = True	
        else:
          escolha_num = arquivos.index(escolha[0])
          episodes = FILES["Files"][escolha_num:]
          escolheu = True
    
    elif escolha[0] == "..":
      if len(anterior) == 0:
        return
      FILES = anterior.pop()

  return episodes


def watch(episodes):
  if returnLinks:
    links = "\n".join([ i["Link"] for i in episodes ])
    pyperclip.copy(links)
    print(links)
    exit()

  if player == "syncplay":
    with open(f'{script_path}/.playlist.txt', 'w') as pl:
      pl.write("\n".join([ f'https://{i["Link"]}' for i in episodes ]))
    os.system(f"syncplay --no-store --load-playlist-from-file '{script_path}/.playlist.txt'")
  else:
    with open(f'{script_path}/.playlist.m3u', 'w') as pl:
      pl.write('#EXTM3U\n')
      for ep in episodes:
        pl.write(f"#EXTINF:0, {ep['Title']}\nhttps://{ep['Link']}\n")
    os.system('i3-msg -q workspace "5. "')
    os.system(f"mpv --fs --playlist={script_path}/.playlist.m3u")

def main():
  while True:
    anime = choose_anime()
    imagem = re.sub(r'[/:&\(\)\-\"\”\“ ]',"", clean_title(anime["Title"]))
    nome = clean_title(anime["Title"])
    episodes = choose_eps(anime)
    if showImages:
      os.system('pkill feh')
    if episodes:
      if not returnLinks:
        os.system(f"dunstify 'AnitsuCli: Started playing' '{nome}' -I {script_path}/Imgs/{imagem}.jpg")
      watch(episodes)


def clean_title(str: str):
  return re.search(r'^.*?(?=(?: DUAL| Blu\-[Rr]ay| \[|$))', str).group()


if __name__ == "__main__":
  main()
