#!/usr/bin/env python3

from urllib.request import quote, unquote
from collections import defaultdict
from time import monotonic
import aiohttp
import asyncio
import json
import re
import os

OCLOUD_URL = "https://www.odrive.com/rest/weblink/list_folder?weblinkUri=/{}"
SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = f"{SCRIPT_PATH}/Anitsu.json"
TAGS_PATH = f"{SCRIPT_PATH}/Tags.json"
CC_TASKS = 100
T_COLUMNS = os.get_terminal_size().columns - 10
START = monotonic()

async def main():
    global db, total_links, session, counter

    with open(DB_PATH, 'r') as file:
        db = json.load(file)

    total_links = len([ j for i in db.values() for j in i['Download'] + i['ODrive'] if 'Tree' not in i.keys()])
    print(f"\n{total_links} Folders to scan!\n")
  
    if total_links == 0: return
    counter = 0
    queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        for index, value in db.items():
            if "Tree" in value.keys(): continue

            db[index]['Tree'] = molde()
      
            for i, link in enumerate(value["Download"] + value['ODrive']):
                if i == 0:
                    queue.put_nowait((True, link, index, value['Title']))
                else:
                    queue.put_nowait((False, link, index, value['Title']))

        tasks = []
        for _ in range(CC_TASKS):
            task = asyncio.create_task(run(queue))
            tasks.append(task)
        await queue.join()
        print()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        with open('Anitsu.json', 'w') as file:
            json.dump(db, file)

async def run(queue: asyncio.Queue):
    while True:
        first, link, index, title = await queue.get()
        if 'odrive' in link:
            await odrive(link, index)
        else:
            await nextcloud(first, link, index, title)

        global counter
        counter += 1
        pbar(counter, total_links, title)
        queue.task_done()

async def odrive(link, index):
    id = link.split('/')[-1]
    async with session.get(OCLOUD_URL.format(id)) as r:
        files = await r.json()
    if 'data' not in files.keys(): return
    temp = db[index]['Tree']['Dirs']['ODrive']['Files']
    for value in reversed(files['data']['items']):
        try:
            download_url = '/'.join(value['downloadUrl'].split('/')[2:])
        except:
            download_url = ''
        temp.append({"Title": value['name'], "Link": download_url})
    
async def nextcloud(first, link, index, title):
    id = link.split('/')[-1]
    url = f'https://{link.split("/")[0]}/nextcloud/public.php/webdav'
    headers = {'Depth': 'infinity'}
    auth = aiohttp.BasicAuth(id, '')

    async with session.request(method="PROPFIND", url=url, headers=headers, auth=auth) as r:
        if r.status != 207: print('\n' + title + '\n')
        text = await r.text()

    files = [ unquote(i) for i in re.findall(r'public.php\/webdav/([^<]+?)</d', text)]

    if not files and 'contenttype>video/' in text:
        async with session.request(method='HEAD', url=url, auth=auth) as r:
            filename = unquote(re.search(r'filename=\"([^\"]*)', r.headers['content-disposition']).group(1))
            await get_files(filename, link, first, index)
    else:
        paths = [ i.split('/') for i in files if i.split('/')[-1] != '']
        await get_files(paths, link, first, index)

async def get_files(paths: list, link: str, first: bool, index: str):
    if type(paths) == str:
        if first:
            db[index]['Tree']['Files'] = [{"Title": paths, "Link": f"{link}/download/{quote(paths)}"}]
        else:
            db[index]['Tree']['Dirs'][paths] = {'Dirs': {}, 'Files': [{"Title": paths, "Link": f"{link}/download/{quote(paths)}"}]}
        return

    if not first:
        dir = await get_name(link)

    for path in paths:
        url = f"{link}/download?path=/"
        temp = db[index]['Tree']
        if not first:
            temp = temp['Dirs'][dir]
        for i in path[:-1]:
            url += quote(i) + "/"
            temp = temp['Dirs'][i]

        temp['Files'].append({"Title": path[-1], "Link": f"{url}/{quote(path[-1])}"})

async def get_name(link: str):
    async with session.get(f"https://{link}") as r:
        texto = await r.text()
        nome = re.findall(r'\<h1 class\=\"header\-appname\"\>\s+(.*)\s+\<\/h1\>', texto.replace('\n',''))[0].strip()
    return nome

def pbar(curr: int, total: int, title: str):
    text = f" => {curr * 100 // total:3}% "
    remain = T_COLUMNS - len(text)
    if len(title) < remain:
        blank = ' ' * (remain - len(title))
    else:
        blank = ''
    text += f"{title[:remain]}"
    print(f"{text}{blank} {monotonic() - START:5.2f}s", end="\r")

def molde():
    return {"Dirs": defaultdict(molde), "Files": []}

if __name__ == "__main__":
    asyncio.run(main())