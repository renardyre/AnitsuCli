#!/usr/bin/env python3

import aiohttp
import asyncio
import json
import os
import re
import html

SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = f"{SCRIPT_PATH}/Anitsu.json"
TAGS_PATH = f"{SCRIPT_PATH}/Tags.json"
WP_URL = "https://anitsu.com.br/wp-json/wp/v2/posts?per_page=100&page={}"
CC_TASKS = 10
T_COLUMNS = os.get_terminal_size().columns // 2
R_NEXTCLOUD = re.compile(r'https?:\/\/(.*?\/nextcloud\/s\/[^\"]{15})')
R_MAL = re.compile(r'https?:\/\/myanimelist\.net\/anime\/(\d*)?\/[^\\]+')
R_ANILIST = re.compile(r'https?:\/\/anilist\.co\/anime\/(\d*)?\/[^\\]+')
R_IMG = re.compile(r'(https?:\/\/.*?\/.*?\.(?:png|jpe?g|webp|gif))')

async def main():
    global db, tags, counter, t_pages, session
    with open(TAGS_PATH, 'r') as fp:
        tags = json.load(fp)
    db = {}
    counter = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(WP_URL.format(1)) as r:
            t_pages = int(r.headers['X-WP-TotalPages'])
            t_posts = int(r.headers['X-WP-Total'])
            posts = await r.json()
        if not posts:
            return
        await update_db(posts)
        print(f"{t_posts} Posts found in {t_pages} pages!\n")

        queue = asyncio.Queue()
        for page in range(2, t_pages+1):
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

async def get_data(queue: asyncio.Queue):
    while True:
        page = await queue.get()
        while True:
            async with session.get(WP_URL.format(page)) as r:
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
        if not links: return 
        db[post['id']] = {
            'Title': html.unescape(post['title']['rendered']),
            'Image': regex(R_IMG, content),
            'Date': post['date'],
            'Modified': post['modified'],
            'Anilist': regex(R_ANILIST, content),
            'MAL': regex(R_MAL, content),
            'Link': post['link'],
            'Download': links,
            'Tags': [ tags[str(i)] for i in post['categories']]
        }

def regex(pattern: re.Pattern, string: str):
    try:
        match = re.search(pattern, string).group(1)
    except:
        match = ''
    return match

def pbar(curr: int):
    prop = curr * 100 // (t_pages-1)
    text = " => {:3}% [ ".format(prop)
    remain = T_COLUMNS - len(text)
    progress = "|" * (prop * remain // 100)
    blank = " " * (remain - len(progress))
    print(f"{text}{progress}{blank} ] ", end="\r")

if __name__ == "__main__":
    asyncio.run(main())