#!/usr/bin/env python3

from shutil import which
from time import monotonic, sleep
from dotenv import load_dotenv, set_key
from datetime import datetime
from getpass import getpass
import downloadImages
import requests
import aiohttp
import asyncio
import json
import html
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(SCRIPT_PATH, "Anitsu.json")
LAST_RUN =  os.path.join(SCRIPT_PATH, ".last_run")
NOW = datetime.isoformat(datetime.now())
START = monotonic()
TAGS_URL = "https://anitsu.moe/wp-json/wp/v2/categories?per_page=100&_fields=id,name"
WP_URL = "https://anitsu.moe/wp-json/wp/v2/posts?per_page=100&page={}&modified_after={}&_fields=id,date,modified,link,title,content,categories"
CC_TASKS = 10
T_COLUMNS = os.get_terminal_size().columns - 10
R_NEXTCLOUD = re.compile(r'https?:\/\/(.*?\/nextcloud\/s\/[^\"]{15})')
R_OCLOUD = re.compile(r'https?:\/\/(www\.odrive\.com\/s\/[^\"]*)')
R_GDR  = re.compile(r'href=\"https\:\/\/(drive\.google[^\"\?]*)')
R_MAL = re.compile(r'https?:\/\/myanimelist\.net\/anime\/(\d*)?\/[^\\]+')
R_ANILIST = re.compile(r'https?:\/\/anilist\.co\/anime\/(\d*)?\/[^\\]+')
R_IMG = re.compile(r'(https?:\/\/.*?\/.*?\.(?:png|jpe?g|webp|gif))')
R_PASSWD = re.compile(r'Senha: \<span.*?\>(.*)\<\/span\>')

async def main():
    global db, tags, counter, t_pages, session, last_run, notifications, auth
    db = {}
    notifications = []

    user, passwd = get_credentials()
    clear_terminal()
    auth = aiohttp.BasicAuth(user, passwd)

    if os.path.exists(DB_PATH) and os.path.exists(LAST_RUN):
        with open(DB_PATH, 'r') as fp:
            db = json.load(fp)

        with open(LAST_RUN, 'r+') as fp:
            last_run = fp.read()
            fp.seek(0)
            fp.write(NOW)
            fp.truncate()
    else:
        with open(LAST_RUN, 'w') as fp:
            last_run = "2000-01-01T00:00:00"
            fp.write(NOW)

    counter = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(TAGS_URL, auth=auth) as t:
            tags = await t.json()
            tags = {i['id']: i['name'] for i in tags}
        async with session.get(WP_URL.format(1, last_run), auth=auth) as r:
            t_pages = int(r.headers['X-WP-TotalPages'])
            t_posts = int(r.headers['X-WP-Total'])
            posts = await r.json()
        if not posts:
            print(f"Up to date!")
            return
        print(f"{t_posts} Posts found in {t_pages} pages!\n")

        queue = asyncio.Queue()
        for page in range(1, t_pages+1):
            queue.put_nowait(page)

        tasks = []
        for _ in range(CC_TASKS):
            task = asyncio.create_task(get_data(queue))
            tasks.append(task)
        await queue.join()
        print()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    with open(DB_PATH, 'w', encoding='utf-8') as fp:
        json.dump(db, fp, ensure_ascii=False)

    downloadImages.main()
    print()
    if len(notifications) < 100:
        for i in notifications:
            info = db[i]
            print(f"- {info['Title']}")
            if which('dunstify'):
                title = clean_title(info['Title'])
                image = i
                link = info['Link']
                os.system(f"if [[ $(dunstify --action='default,Reply' 'AnitsuCli' '{title}' -I {SCRIPT_PATH}/Imgs/{image}.jpg) -eq 2 ]]; then firefox {link}; fi &")
            sleep(0.1)

async def get_data(queue: asyncio.Queue):
    while True:
        page = await queue.get()
        while True:
            async with session.get(WP_URL.format(page, last_run), auth=auth) as r:
                st_code = r.status
                if st_code == 200:
                    posts = await r.json()
                    break
        global counter
        counter += 1
        await update_db(posts)
        pbar(counter)
        queue.task_done()

async def update_db(posts: dict):
    for post in posts:
        content = post['content']['rendered']
        links = list(set(re.findall(R_NEXTCLOUD, content)))
        odrive_links = re.findall(R_OCLOUD, content)
        gd_links = list(set(re.findall(R_GDR, content)))
        if not links and not odrive_links and not gd_links: continue
        notifications.append(post['id'])
        db[post['id']] = {
            'Title': html.unescape(post['title']['rendered']),
            'Image': regex(R_IMG, content),
            'Description': description(post['content']['rendered']),
            'Date': post['date'],
            'Modified': post['modified'],
            'Password': regex(R_PASSWD, post['content']['rendered']),
            'Anilist': regex(R_ANILIST, content),
            'MAL': regex(R_MAL, content),
            'Link': post['link'],
            'Download': links,
            'ODrive': odrive_links,
            'GDrive': gd_links,
            'Tags': [ tags[i] for i in post['categories']]
        }

def regex(pattern: re.Pattern, string: str):
    try:
        match = re.search(pattern, string).group(1)
    except:
        match = ''
    return match

def pbar(curr: int):
    prop = curr * 100 // (t_pages)
    text = f" => {prop:3}% "
    remain = T_COLUMNS - len(text) - 4
    progress = "|" * (prop * remain // 100)
    blank = " " * (remain - len(progress))
    print(f"{text}[ {progress}{blank} ] {monotonic() - START:5.2f}s", end="\r")

def description(text: str):
    desc = html.unescape(text)
    desc = desc.replace('<hr />', '\n')
    desc = re.sub(r'\<br.*?\>', '\n', desc)
    desc = re.sub(r'\<.*?\>', '', desc)
    info = re.sub(r'\n[\n|\s]*', '\n', desc)
    info = info.replace('Sinopse', '\nSinopse').strip().replace('\n', 'NeLi')
    info = re.sub(r'(Sinopse:.*?NeLi).*', r'\1', info)
    return info

def clean_title(str: str):
  return re.search(r'^.*?(?=(?: Multi| Trial| DUAL| Blu\-[Rr]ay| \[|$))', str).group()

def clear_terminal():
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')

def input_credentials():
    print("Por favor insira seus dados de login!")
    username = input("Usuário: ")
    passwd = getpass("Senha: ")
    return username, passwd

def set_credentials(username, passwd):
    set_key('.env', 'ANITSU_USERNAME', username)
    set_key('.env', 'ANITSU_PASSWD', passwd)

def get_credentials():
    load_dotenv()
    username = os.getenv("ANITSU_USERNAME")
    passwd = os.getenv("ANITSU_PASSWD")
    logged = False
    test_url = "https://anitsu.moe/wp-json/wp/v2/users/1?_fields=id"
    while not logged:
        if not username or not passwd:
            username, passwd = input_credentials()
        logged = requests.get(test_url, auth=(username, passwd)).status_code == 200
        if not logged:
            clear_terminal()
            print("Usuário e/ou senha inválidos!")
            username, passwd = '', ''
    set_credentials(username, passwd)
    return (username, passwd)

if __name__ == "__main__":
    asyncio.run(main())
