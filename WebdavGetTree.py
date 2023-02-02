#!/usr/bin/env python3

from urllib.request import quote, unquote
from collections import defaultdict
from time import monotonic
from shutil import which
import aiohttp
import asyncio
import json
import re
import os

OCLOUD_URL = "https://www.odrive.com/rest/weblink/list_folder?weblinkUri=/{}"
GDRIVE_URL = "drive.google.com/u/0/uc?id={}&export=download&confirm=t"
FILES_NEXT = re.compile(r'<d:response><d:href>/nextcloud/public.php/webdav/([^<]+?[^/])</d:href>.*?<d:getcontentlength>(.*?)</d:getcontentlength>.*?</d:response>')
SCRIPT_PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(SCRIPT_PATH, "Anitsu.json")
TAGS_PATH = os.path.join(SCRIPT_PATH, "Tags.json")
CC_TASKS = 100
T_COLUMNS = os.get_terminal_size().columns - 10
START = monotonic()

async def main():
    global db, total_links, session, counter, rclone

    rclone = which('rclone')

    with open(DB_PATH, 'r') as file:
        db = json.load(file)

    total_links = len([ j for i in db.values() for j in i['Download'] + i['ODrive'] + i['GDrive'] if 'Tree' not in i.keys()])
    print(f"\n{total_links} Folders to scan!\n")
  
    if total_links == 0: return
    counter = 0
    queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        for index, value in db.items():
            if "Tree" in value.keys(): continue

            db[index]['Tree'] = molde()
      
            for i, link in enumerate(value["Download"] + value['ODrive'] + value['GDrive']):
                if i == 0:
                    queue.put_nowait((True, link, index, value['Title'], value['Password']))
                else:
                    queue.put_nowait((False, link, index, value['Title'], value['Password']))

        tasks = []
        for _ in range(CC_TASKS):
            task = asyncio.create_task(run(queue))
            tasks.append(task)
        await queue.join()
        print()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        with open(DB_PATH, 'w', encoding='utf-8') as file:
            json.dump(db, file)

async def run(queue: asyncio.Queue):
    while True:
        first, link, index, title, passwd = await queue.get()
        try:
            if 'odrive' in link:
                pass
                #await odrive(link, index)
            elif 'drive.google.com/drive/folders' in link and rclone:
                await gdrive(link, index)
            elif 'drive.google.com/file' in link:
                pass
            elif 'cloud.anitsu' in link:
                await nextcloud(first, link, index, title, passwd)
        except Exception as e:
            print(f"{link} - {e}")

        global counter
        counter += 1
        pbar(counter, total_links, title)
        queue.task_done()

async def gdrive(link:str, index:str):
    id = link.split('/')[-1]
    proc = await asyncio.create_subprocess_shell(" ".join([
            'rclone', 'lsjson', '-R', '--files-only',
            '--no-modtime', '--no-mimetype',
            '--drive-root-folder-id', id, 'Anitsu:'
        ]), stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    files = json.loads(stdout.decode())
    for f in files:
        path = f["Path"].split('/')
        size = int(f["Size"])
        id = f["ID"]
        temp = db[index]['Tree']['Dirs']['Google Drive']
        db[index]['Tree']['Size'] += size
        temp['Size'] += size
        for p in path[:-1]:
            temp = temp['Dirs'][p]
            temp['Size'] += size
        temp['Files'].append({"Title": path[-1], "Link": GDRIVE_URL.format(id), "Size": size})

async def odrive(link:str, index:str):
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
    
async def nextcloud(first:bool, link:str, index:str, title:str, passwd:str):
    link = link.replace('anitsu.com.br', 'anitsu.moe')
    id = link.split('/')[-1]
    url = f'https://{link.split("/")[0]}/nextcloud/public.php/webdav'
    headers = {'Depth': 'infinity'}
    auth = aiohttp.BasicAuth(id, passwd)

    async with session.request(method="PROPFIND", url=url, headers=headers, auth=auth) as r:
        if r.status != 207:
            print('\n' + title + '\n')
            return
        text = await r.text()

    files = re.search(r'[^/]\<\/d\:href\>', text)

    if not files and 'contenttype>video/' in text:
        async with session.request(method='HEAD', url=url, auth=auth) as r:
            filename = unquote(re.search(r'filename=\"([^\"]*)', r.headers['content-disposition']).group(1))
            size = r.headers['content-length']
            await get_files(f"{filename}\t{size}", link, first, index)
    else:
        data = re.findall(FILES_NEXT, text)
        paths = [ (unquote(i).split('/'), j) for i, j in data ]
        await get_files(paths, link, first, index)

async def get_files(paths: list, link: str, first: bool, index: str):
    if type(paths) == str:
        name, size = paths.split('\t')
        db[index]['Tree']['Size'] += int(size)
        if first:
            db[index]['Tree']['Files'] = [{"Title": name, "Link": f"{link}/download/{quote(name)}", "Size": int(size)}]
        else:
            db[index]['Tree']['Dirs'][name]['Size'] += int(size)
            db[index]['Tree']['Dirs'][name] = {'Dirs': {}, 'Files': [{"Title": name, "Link": f"{link}/download/{quote(name)}", "Size": int(size)}]}
        return

    if not first:
        dir = await get_name(link)

    for path, size in paths:
        url = f"{link}/download?path=/"
        temp = db[index]['Tree']
        temp['Size'] += int(size)
        if not first:
            temp = temp['Dirs'][dir]
            temp['Size'] += int(size)
        for i in path[:-1]:
            url += quote(i) + "/"
            temp = temp['Dirs'][i]
            temp['Size'] += int(size)

        temp['Files'].append({"Title": path[-1], "Link": f"{url}{quote(path[-1])}", "Size": int(size)})

async def get_name(link: str):
    async with session.get(f"https://{link}") as r:
        texto = await r.text()
        nome = re.findall(r'\<h1 class\=\"header\-appname\"\>\s*(.*)\s*\<\/h1\>', texto.replace('\n',''))[0].strip()
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
    return {"Dirs": defaultdict(molde), "Files": [], "Size": 0}

if __name__ == "__main__":
    asyncio.run(main())
