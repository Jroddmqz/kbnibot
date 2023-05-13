import asyncio
import math
import os
import random
import string
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pymongo import DESCENDING
from pyrogram import filters

from ubot import app, bot, bot2, Mclient
from ubot.utils.misc import upload_from_queue, is_chat

if bot2:
    uploader = bot2

temp = '.temp/'
if not os.path.exists(temp):
    os.makedirs(temp)


@bot.on_message(filters.command(["r34"], prefixes=[".", "/"]) & filters.incoming)
async def r34(client, message):

    async def get_rule():
        rule=[]
        rule.append(["honkai:_star_rail", "-1001407356398", "😈 https://t.me/+4wqeR0dRySJlMDUx"])  # leeching group
        rule.append(["genshin_impact", "-1001629528057", "😈 https://t.me/+45f-VAxVB2NjN2Jh"])
        # url.append(["", ""])
        return rule

    async def process(rule):
        api_rule_url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&tags="
        soup = BeautifulSoup(requests.get(f"{api_rule_url}{rule[0]}").content, "lxml-xml")
        count = soup.posts.attrs['count']

        var = 0
        post = []
        while var <= math.ceil(int(count) / 100):
            x_rule = f"{api_rule_url}{rule[0]}&pid={var}"
            soup = BeautifulSoup(requests.get(x_rule).content, "lxml-xml")
            for x in soup.posts:
                if x == '\n':
                    continue
                post.append(x)
            var += 1
            await asyncio.sleep(1)

        collection = db[f'{rule[0]}']

        for x in post:
            item = {"id": x.get('id'), "file_url": x.get('file_url'), "source": x.get('source'), "tag": rule[0], "published": False}
            exist = collection.find_one({"id": x.get('id')})
            if not exist:
                collection.insert_one(item)

        _chat_id = await is_chat(app, rule[1])
        if _chat_id is None:
            print(f"error chat id {_chat_id}")
            return

        print(f"{rule[0]} --- {count}items --- Posting to{_chat_id}")

        items = collection.find().sort([("$natural", DESCENDING)])

        for x in items:
            if not x['published']: #if x['published'] == False:
                archive = x['file_url']
                response = requests.get(archive)
                if response.status_code == 200:
                    path_, ext_ = os.path.splitext(archive)
                    now = datetime.now()
                    date_time = now.strftime("%y%m%d_%H%M%S")
                    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
                    filename = f"{date_time}{random_chars}{ext_}"

                    with open(os.path.join(temp, filename), "wb") as f:
                        f.write(response.content)

                    url = x['source']
                    source = f"[source]({url})"
                    capy = source + "\n" + rule[2]
                    filepath = f"{temp}{filename}"

                    await queue.put((uploader, filepath, _chat_id, capy, ext_, x))

        upload_task = asyncio.create_task(upload_from_queue(queue))

    queue = asyncio.Queue()
    db = Mclient["rule"]
    ruler = await get_rule()

    while True:
        tasks = [asyncio.create_task(process(rule)) for rule in ruler]
        await asyncio.gather(*tasks)
        await queue.join()
        await asyncio.sleep(86400)
