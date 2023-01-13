# AnitsuCli
![Cover](https://cdn.discordapp.com/attachments/1028636320190443570/1028636414025420872/unknown.png)

### Third-Party Dependencies
- [fzf](https://github.com/junegunn/fzf)
- [mpv](https://github.com/mpv-player/mpv)
- [feh](https://github.com/derf/feh)*
- [aria2](https://github.com/aria2/aria2)*
- [imagemagick](https://github.com/ImageMagick/ImageMagick)*

*Optional

## Setup
#### For Windows Users
> It's required to have [fzf](https://github.com/junegunn/fzf/releases) and [mpv](https://mpv.io/installation/) installed. You can put theirs binaries inside AnitsuCli folder if you don't want to install them.

### Create .env File
```env
ANITSU_USERNAME=""
ANITSU_PASSWD=""
ARIA_URL=""     #Optional 
ARIA_TOKEN=""   #Optional
```

### Install Requirements and Run
```bash
git clone https://github.com/renardyre/AnitsuCli
cd AnitsuCli
pip install -r requirements.txt
chmod +x *py
./AnitsuCli.py -h
```

![preview](preview.gif)
