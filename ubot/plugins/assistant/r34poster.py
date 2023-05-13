import os
import time
import math
import asyncio
import logging
import requests
import feedparser
import random, string
from pyrogram import filters
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse
from ubot import app, bot, Mclient
from ubot.utils.misc import resizer#, # is_chat
from ubot.utils.san import Bruteforce
from pymongo import ASCENDING, DESCENDING


temp = '.temp/'
if not os.path.exists(temp):
    os.makedirs(temp)


@bot.on_message(filters.command(["r34"], prefixes=[".","/"]) & filters.incoming)
async def r34(client, message):

    async def is_chat(item):
        try:
            chat_id = int(item)
            try:
                chat = await app.get_chat(chat_id)
            except:
                return None
            chat_id = chat.id
        except ValueError:
            if not item.startswith("@"):
                return None
            try:
                chat = await app.get_chat(item)
            except:
                return None
            chat_id = chat.id
        return chat_id
    def get_rule():
        rule = []
        rule.append(["honkai:_star_rail", "-1001655727761", "@star_rail"]) #leeching group
        rule.append(["genshin_impact", "-1001655727761", "@gensin_impact"])
        #url.append(["", ""])
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
            item = {"id": x.get('id'), "file_url": x.get('file_url'), "source": x.get('source'), "published": False}
            exist = collection.find_one({"id": x.get('id')})
            if not exist:
                collection.insert_one(item)

        chatid = await is_chat(rule[1])
        if chatid is None:
            print(f"error chat id {chatid}")
            return

        print(f"{rule[0]} --- {count}items --- Posting to{chatid}")

        items = collection.find().sort([("$natural", DESCENDING)])

        for x in items:
            if x['published'] == False:
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
                    value = f"{x['source']}"
                    capy = value + rule[2]

                    if ext_.lower() in {'.jpg', '.png', '.webp', '.jpeg'}:
                        new_file = resizer(f"{temp}{filename}")
                        try:
                            sended = await bot.send_photo(chatid, photo=new_file, caption=str(capy))
                            await asyncio.sleep(1)
                            await bot.send_document(chatid, document=f"{temp}{filename}")
                        except:
                            try:
                                sended = await bot.send_document(chatid, document=f"{temp}{filename}", caption=str(capy))
                            except Exception as e:
                                logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

                        if os.path.exists(new_file):
                            os.remove(new_file)
                    elif ext_.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
                        try:
                            sended = await bot.send_video(chatid, video=f"{temp}{filename}", caption=str(capy))
                            await asyncio.sleep(1)
                            await bot.send_document(chatid, document=f"{temp}{filename}")
                        except:
                            try:
                                sended = await bot.send_document(chatid, document=f"{temp}{filename}", caption=str(capy))
                            except Exception as e:
                                logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
                    else:
                        try:
                            sended = await bot.send_document(chatid, document=f"{temp}{filename}", caption=str(capy))
                        except Exception as e:
                            logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

                    if sended != None:
                        if not x['published']:
                            filter = {'id': x['id']}
                            update = {'$set': {'published': True}}
                            result = collection.update_one(filter, update)


                    os.remove(f"{temp}{filename}")
                    await asyncio.sleep(60)



    db = Mclient["rule"]
    ruler = get_rule()
    while True:
        tasks = [asyncio.create_task(process(rule)) for rule in ruler]

        await asyncio.gather(*tasks)
        #print(last_checked_time_g)
        await asyncio.sleep(86400)
