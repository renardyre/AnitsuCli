# AnitsuCli
![Cover](https://cdn.discordapp.com/attachments/1028636320190443570/1028636414025420872/unknown.png)

## Dependências
- [fzf](https://github.com/junegunn/fzf)
- [mpv](https://github.com/mpv-player/mpv)
- [feh](https://github.com/derf/feh)*
- [rclone](https://rclone.org)*
- [aria2](https://github.com/aria2/aria2)*
- [imagemagick](https://github.com/ImageMagick/ImageMagick)*

*Opcional


## Funcionalidades
```
Flags:
-l, --links    Em vez de reproduzir, copia os links de download (Se configurado, inicia o download no aria).
-t, --tags     Seleciona tags.
-u, --update   Atualiza a base de dados.
-v, --version  Mostra a versão do programa.
-h, --help     Mostra a mensagem de ajuda.

Bindings:
ctrl-p         Ativa preview de info e imagem do post, se disponível.
ctrl-f         Ativa preview de arquivos do post, se disponível.
ctrl-w         Ativa ou desativa a quebra de linha automática do preview.
ctrl-a         Seleciona todos os arquivos mostrados.
```

## Setup
#### Usuários de Windows
> É necessário ter [fzf](https://github.com/junegunn/fzf/releases) e [mpv](https://mpv.io/installation/) instalado. Você pode instalar os programas, ou baixar os binários e colocá-los dentro da pasta AnitsuCli.

#### Suporte para Google Drive
> Para ter suporte, você terá que criar um remote no rclone chamado: `Anitsu`. Siga instruções [aqui](https://rclone.org/drive/).

#### Crie o arquivo `.env`
```env
ANITSU_USERNAME=""  #Seu usuário na Anitsu
ANITSU_PASSWD=""    #Sua Senha na Anitsu
ARIA_URL=""         #Opcional
ARIA_TOKEN=""       #Opcional
```

#### Instale os requisitos e rode o programa
```bash
git clone https://github.com/renardyre/AnitsuCli
cd AnitsuCli
pip install -r requirements.txt
chmod +x *py
./AnitsuCli.py -h
```

![preview](preview.gif)
