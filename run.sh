#/usr/bin/env bash

function cleanup() {
    tput cnorm
}

trap cleanup EXIT
clear
tput civis

python3 PostsAnitsu.py
dunstify "AnitsuCli" "Atualização da Lista de Animes Completa" -I Imgs/LogoAnitsu.png
python3 WebdavGetTree.py
dunstify "AnitsuCli" "Base de Dados Atulizada com Sucesso!" -I Imgs/LogoAnitsu.png