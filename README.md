# AnitsuCli
[![Cover](https://cdn.discordapp.com/attachments/1028636320190443570/1028636414025420872/unknown.png)](https://anitsu.moe)

O AnitsuCli é uma interface de linha de comando escrita em [Python](https://www.python.org/) para o site de anime [Anitsu](https://anitsu.moe). Ele permite aos usuários pesquisar e reproduzir episódios de anime diretamente do terminal. Utilize com sabedoria e bom senso!

Nota: Certifique-se de que você tem todas as dependências essênciais instaladas e seguiu as etapas de configuração corretamente antes de executar o programa. Caso tenha alguma dúvida ou encontre um problema, sinta-se à vontade para abrir uma issue no repositório do projeto.

## Funcionalidades
- Pesquisa e reprodução de animes.
- Copia links de download para baixar os episódios (Se configurado, inicia o download no aria2).
- Filtragem de animes a partir de tags. (Ex: Slice of Life, Isekai...)
- Exibição de informações e imagens do anime.
- Suporte a armazenamento em nuvem do Google Drive.

## Dependências
#### Essenciais
- [python](https://www.python.org/) é a linguagem na qual o programa é escrito.
- [fzf](https://github.com/junegunn/fzf) é necessário para a pesquisa e seleção de episódios.
- [mpv](https://github.com/mpv-player/mpv) é necessário para reproduzir os episódios.
#### Opcionais
- [ueberzug](https://github.com/doytsujin/ueberzug) ou [feh](https://github.com/derf/feh) são usados para exibir as capas dos animes.
- [rclone](https://rclone.org) é usado para suporte de armazenamento em nuvem do Google Drive.
- [aria2](https://github.com/aria2/aria2) é usado para baixar os episódios.
- [imagemagick](https://github.com/ImageMagick/ImageMagick) é usado para redimensionar as capas dos animes.

## Setup
No diretório raiz do projeto, crie um arquivo chamado `.env`. Adicione as seguintes linhas e preencha com as suas credenciais:
```env
ANITSU_USERNAME=""  #Seu usuário na Anitsu
ANITSU_PASSWD=""    #Sua Senha na Anitsu
ARIA_URL=""         #Opcional (Download automático pelo aria2)
ARIA_TOKEN=""       #Opcional (Download automático pelo aria2)
ARIA_DIR=""         #Opcional (Pasta padrão de download, usa o caminho inteiro do arquivo)
```

#### Usuários de Windows
> É necessário ter [fzf](https://github.com/junegunn/fzf/releases) e [mpv](https://mpv.io/installation/) instalados. Você pode instalar os programas através de seus instaladores, ou se preferir, baixar os binários e colocá-los dentro da pasta AnitsuCli.

#### Suporte para Google Drive
> Para ter suporte, você terá que criar um remote no rclone chamado: `Anitsu`. Siga instruções [aqui](https://rclone.org/drive/).

#### Instale os requisitos e rode o programa
1. Baixe o repositório do AnitsuCli usando o comando `git clone https://github.com/renardyre/AnitsuCli`
2. Entre na pasta do projeto com `cd AnitsuCli`
3. Rode o comando `pip install -r requirements.txt` para instalar as dependências do projeto.
4. Altere as permissões dos arquivos .py com `chmod +x *.py`
5. Rode o programa usando `python AnitsuCli.py -h` para ver as opções de comando.

## Flags e Bindings
```
Flags:
-l, --links    Em vez de reproduzir, copia os links de download (Se configurado, inicia o download no aria).
-t, --tags     Seleciona tags.
-u, --update   Atualiza a base de dados.
-v, --version  Mostra a versão do programa.
-h, --help     Mostra a mensagem de ajuda.

Bindings:
ctrl-p         Ativa preview de info e imagem do anime, se disponível.
ctrl-f         Ativa preview de arquivos do anime, se disponível.
ctrl-w         Ativa ou desativa a quebra de linha automática do preview.
ctrl-a         Seleciona todos os arquivos mostrados.
```

![preview](preview.gif)
