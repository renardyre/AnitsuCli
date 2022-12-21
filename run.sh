#/usr/bin/env bash

function cleanup() {
    tput cnorm
}

if [[ $1 == 'full' ]]; then
    rm -f Anitsu.json
    echo "2000-01-01T00:00:00" > LastRun.txt
fi



trap cleanup EXIT
clear
tput civis

python3 PostsAnitsu.py
dunstify "AnitsuCli" "Atualização da Lista de Animes Completa" -I Imgs/LogoAnitsu.png > /dev/null 2>&1
python3 WebdavGetTree.py
dunstify "AnitsuCli" "Base de Dados Atulizada com Sucesso!" -I Imgs/LogoAnitsu.png > /dev/null 2>&1
