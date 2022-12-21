#!/usr/bin/env python3

from datetime import datetime
from time import monotonic, sleep
from dotenv import load_dotenv
import downloadImages
import aiohttp
import asyncio
import json
import html
import os
import re

SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = f"{SCRIPT_PATH}/Anitsu.json"
TAGS_PATH = f"{SCRIPT_PATH}/Tags.json"
LAST_RUN = f"{SCRIPT_PATH}/LastRun.txt"
NOW = datetime.isoformat(datetime.now())
START = monotonic()
WP_URL = "https://anitsu.moe/wp-json/wp/v2/posts?per_page=100&page={}&modified_after={}"
CC_TASKS = 10
T_COLUMNS = os.get_terminal_size().columns - 10
R_NEXTCLOUD = re.compile(r'https?:\/\/(.*?\/nextcloud\/s\/[^\"]{15})')
R_OCLOUD = re.compile(r'https?:\/\/(www\.odrive\.com\/s\/[^\"]*)')
R_MAL = re.compile(r'https?:\/\/myanimelist\.net\/anime\/(\d*)?\/[^\\]+')
R_ANILIST = re.compile(r'https?:\/\/anilist\.co\/anime\/(\d*)?\/[^\\]+')
R_IMG = re.compile(r'(https?:\/\/.*?\/.*?\.(?:png|jpe?g|webp|gif))')
R_PASSWD = re.compile(r'Senha: \<span.*?\>(.*)\<\/span\>')

async def main():
    global db, tags, counter, t_pages, session, last_run, notifications, auth
    db = {}
    notifications = []

    load_dotenv()
    username = os.getenv("USERNAME")
    passwd = os.getenv("PASSWD")
    auth = aiohttp.BasicAuth(username, passwd)

    with open(LAST_RUN, 'r+') as fp:
        last_run = fp.read()
        fp.seek(0)
        fp.write(NOW)
        fp.truncate()
    with open(TAGS_PATH, 'r') as fp:
        tags = json.load(fp)
    if os.path.exists("Anitsu.json"):
        with open(DB_PATH, 'r') as fp:
            db = json.load(fp)

    counter = 0
    async with aiohttp.ClientSession() as session:
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

    with open(DB_PATH, 'w') as fp:
        json.dump(db, fp)

    downloadImages.main()
    if len(notifications) > 100: return
    print()
    for i in notifications:
        info = db[i]
        print(f"- {info['Title']}")
        title = clean_title(info['Title'])
        image = i
        link = info['Link']
        os.system(f"if [[ $(dunstify --action='default,Reply' 'AnitsuCli' '{title}' -I Imgs/{image}.jpg) -eq 2 ]]; then firefox {link}; fi &")
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
        links = re.findall(R_NEXTCLOUD, content)
        odrive_links = re.findall(R_OCLOUD, content)
        if not links and not odrive_links: continue
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
            'Tags': [ tags[str(i)] for i in post['categories']]
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
    items = desc.split('<hr />')
    if len(items) < 2: return ''
    info = re.sub(r'\<.*?\>', '', items[0]).strip().replace('\n', 'NeLi')
    sinopse = re.sub(r'\<.*?\>', '', items[1]).strip().replace('\n', 'NeLi')
    return f"{info}NeLiNeLi{sinopse}"

def clean_title(str: str):
  return re.search(r'^.*?(?=(?: DUAL| Blu\-[Rr]ay| \[|$))', str).group()

if __name__ == "__main__":
    asyncio.run(main())
