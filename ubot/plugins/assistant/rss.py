import asyncio
import logging
import os
import random
import string
import time
from datetime import datetime

import feedparser
import requests
from dateutil.parser import parse
from pyrogram import filters

from ubot import app, bot, Mclient, log_group
from ubot.utils.misc import resizer, is_chat
from ubot.utils.san import Bruteforce
from input import rss

temp = '.temp/'
if not os.path.exists(temp):
    os.makedirs(temp)

global last_checked_time_g
w = []
for x in rss:
    w.append(time.time())
last_checked_time_g = w


@bot.on_message(filters.command(["rss"], prefixes=[".", "/"]) & filters.incoming)
async def ars(client, message):
    regi = "`Ejecutando rss:`"
    await bot.send_message(log_group, regi)

    async def get_feed_entries_ranked(url):
        entries = []
        feed = feedparser.parse(url)
        if feed['feed']['title'] in 'Danbooru: order:rank':
            order_rank = "rank"
        else:
            order_rank = ""

        for entry in feed.entries:
            entry_data = {
                "title": entry.title,
                "link": entry.link,
                "updated": entry.updated,
                "author": entry.author,
                "order_rank": order_rank,
            }
            entries.append(entry_data)
        return entries

    async def get_feed_entries(url):
        entries = []
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if "danbooru" in url:
                entry_data = {
                    "title": entry.title,
                    "link": entry.link,
                    "updated": entry.updated,
                    "author": entry.author,
                }
                entries.append(entry_data)
            elif "lolibooru" in url:
                entry_data = {
                    "title": entry.title,
                    "link": entry.link,
                    "updated": entry.updated,
                    "author": entry.author,
                }
                entries.append(entry_data)
            else:
                entry_data = {
                    "title": entry.title,
                    "link": entry.link,
                    "updated": entry.updated,
                    "author": entry.author,
                }
                entries.append(entry_data)

        return entries

    async def get_recent_entries_async(url, last_checked_time=None):
        entries = await get_feed_entries(url)
        # print(len(entries))
        recent_entries = []
        current_time = time.time()
        # if last_checked_time is None:
        #    last_checked_time = current_time
        for entry_ in entries:
            published_time = parse(entry_["updated"]).timestamp()
            if last_checked_time < published_time <= current_time:
                # print(f"{last_checked_time} < {published_time} <= {current_time}")
                recent_entries.append(entry_)
        return recent_entries, current_time

    async def process_rss(url):
        _chat_id = None
        chats = rss
        var = 0
        for x in chats:
            if x['rss_url'] != url:
                var += 1
            else:
                _chat_id = await is_chat(app, x['channel'])
                var = var
                collection = db[f'{_chat_id}']
                break
        if _chat_id is None:
            print("error")
            return

        b = Bruteforce()
        global last_checked_time_g

        feed_ = feedparser.parse(url)
        if feed_['feed']['title'] in 'Danbooru: order:rank':
            entries = []
            entries_temp = await get_feed_entries_ranked(url)
            for x in entries_temp:
                item = {"title": x['title'], "link": x['link'], "updated": x['updated'], "author": x['author'],
                        "order": x['order_rank']}
                exist = collection.find_one({"link": x["link"]})
                if not exist:
                    collection.insert_one(item)
                    entries.append(x)
            # if len(entries) > 0:
            #    #print(f"RSS: {var} URL: {url} --- Nuevas entradas: {len(entries)} --- ranked")
            #    regi = f"RSS: {var} URL: {url} --- Nuevas entradas: {len(entries)} --- ranked"
            #    await bot.send_message(log_group, regi)
        else:
            entries, last_checked_time_g[var] = await get_recent_entries_async(url, last_checked_time_g[var])
            # if len(entries) > 0:
            #    #print(f"RSS: {var} URL: {url} --- Nuevas entradas: {len(entries)}")
            #    regi = f"RSS: {var} URL: {url} --- Nuevas entradas: {len(entries)}"
            #    await bot.send_message(log_group, regi)

        for entry in entries:
            try:
                # print(f"{entry['title']}: {entry['link']}")
                if 'danbooru' in entry['link']:
                    archive = b.danbooru(entry['link'])
                elif 'lolibooru' in entry['link']:
                    archive = b.booru(entry['link'], site="lolibooru")
                    archive = archive.replace(" ", "%20")
                elif 'konachan' in entry['link']:
                    archive = b.konachan(entry['link'])
                    archive = archive.replace(" ", "%20")
                elif 'yande.re' in entry['link']:
                    archive = b.booru(entry['link'], site='yandere')
                else:
                    continue
            except Exception as e:
                logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
                continue

            response = requests.get(archive)
            if response.status_code == 200:
                # filename = os.path.basename(archive)
                path_, ext_ = os.path.splitext(archive)
                now = datetime.now()
                date_time = now.strftime("%y%m%d_%H%M%S")
                random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
                filename = f"{date_time}{random_chars}{ext_}"
                with open(os.path.join(temp, filename), "wb") as f:
                    f.write(response.content)
                if ext_.lower() in {'.jpg', '.png', '.webp', '.jpeg'}:
                    new_file = resizer(f"{temp}{filename}")
                    try:
                        await bot.send_photo(_chat_id, photo=new_file, caption=entry['title'])
                        await asyncio.sleep(1)
                        await bot.send_document(_chat_id, document=f"{temp}{filename}")
                    except:
                        try:
                            await bot.send_document(_chat_id, document=f"{temp}{filename}", caption=entry['title'])
                        except Exception as e:
                            logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

                    if os.path.exists(new_file):
                        os.remove(new_file)
                elif ext_.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
                    try:
                        await bot.send_video(_chat_id, video=f"{temp}{filename}", caption=entry['title'])
                        await asyncio.sleep(1)
                        await bot.send_document(_chat_id, document=f"{temp}{filename}")
                    except:
                        try:
                            await bot.send_document(_chat_id, document=f"{temp}{filename}", caption=entry['title'])
                        except Exception as e:
                            logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
                else:
                    try:
                        await bot.send_document(_chat_id, document=f"{temp}{filename}", caption=entry['title'])
                    except Exception as e:
                        logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
                os.remove(f"{temp}{filename}")
            else:
                print("Error al descargar la imagen.")

    rss_urls = rss

    db = Mclient["rss"]

    while True:
        tasks = [asyncio.create_task(process_rss(url['rss_url'])) for url in rss_urls]
        await asyncio.gather(*tasks)
        await asyncio.sleep(60)
