import os
import time
import asyncio
import logging
import requests
import feedparser
import random, string
from pyrogram import filters
from datetime import datetime
from dateutil.parser import parse
from ubot import app, bot, Mclient
from ubot.utils.misc import resizer
from ubot.utils.san import Bruteforce


temp = '.temp/'
if not os.path.exists(temp):
    os.makedirs(temp)


def get_feed_url():
    urls_ = []
    urls_.append(["https://danbooru.donmai.us/posts.atom", "-1001655727761"])
    urls_.append(["https://lolibooru.moe/post.atom", "-1001754747705"])
    urls_.append(["https://siftrss.com/f/9Mn0Rq9QgG", "-1001616034175"]) #@nyastrixroom
    urls_.append(["https://konachan.com/post/atom", "-1001850075721"]) #Konachan
    urls_.append(["https://yande.re/post/atom?tags=", "@acgnxse"])
    return urls_

global last_checked_time_g
w =[]
for x in get_feed_url():
    w.append(time.time())
last_checked_time_g = w


@bot.on_message(filters.command(["rss"], prefixes=[".","/"]) & filters.incoming)
async def ars(client, message):
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


    async def get_feed_entries_ranked(url):
        entries =[]
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
        #print(len(entries))
        recent_entries = []
        current_time = time.time()
        #if last_checked_time is None:
        #    last_checked_time = current_time
        for entry_ in entries:
            published_time = parse(entry_["updated"]).timestamp()
            if last_checked_time < published_time <= current_time:
                #print(f"{last_checked_time} < {published_time} <= {current_time}")
                recent_entries.append(entry_)
        return recent_entries, current_time


    async def process_rss(url):
        chats = get_feed_url()
        var = 0
        for x in chats:
            if x[0] != url:
                var += 1
            else:
                chatid = await is_chat(x[1])
                var = var
                collection = db[f'{chatid}']
                break
        if chatid == None:
            print("error")
            return

        b = Bruteforce()
        global last_checked_time_g

        feed_ = feedparser.parse(url)
        if feed_['feed']['title'] in 'Danbooru: order:rank':
            entries = []
            entries_temp = await get_feed_entries_ranked(url)
            for x in entries_temp:
                item = {"title": x['title'], "link": x['link'], "updated": x['updated'], "author": x['author'], "order": x['order_rank']}
                exist = collection.find_one({"link": x["link"]})
                if not exist:
                    collection.insert_one(item)
                    entries.append(x)
            print(f"RSS: {var} URL: {url} --- Nuevas entradas: {len(entries)} --- ranked")
        else:
            entries, last_checked_time_g[var] = await get_recent_entries_async(url,last_checked_time_g[var])
            print(f"RSS: {var} URL: {url} --- Nuevas entradas: {len(entries)}")

        for entry in entries:
            #print(f"{entry['title']}: {entry['link']}")
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
                archive = ""

            response = requests.get(archive)
            if response.status_code == 200:
                #filename = os.path.basename(archive)
                path_, ext_ = os.path.splitext(archive)
                now = datetime.now()
                date_time = now.strftime("%Y%m%d_%H%M%S")
                random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
                filename = f"{date_time}{random_chars}{ext_}"
                with open(os.path.join(temp, filename), "wb") as f:
                    f.write(response.content)
                if ext_.lower() in {'.jpg', '.png', '.webp', '.jpeg'}:
                    new_file = resizer(f"{temp}{filename}")
                    try:
                        await app.send_photo(chatid, photo=new_file, caption=entry['title'])
                        await asyncio.sleep(1)
                        await app.send_document(chatid, document=f"{temp}{filename}")
                    except:
                        try:
                            await app.send_document(chatid, document=f"{temp}{filename}", caption=entry['title'])
                        except Exception as e:
                            logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

                    if os.path.exists(new_file):
                        os.remove(new_file)
                elif ext_.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
                    try:
                        await app.send_video(chatid, video=f"{temp}{filename}", caption=entry['title'])
                        await asyncio.sleep(1)
                        await app.send_document(chatid, document=f"{temp}{filename}")
                    except:
                        try:
                            await app.send_document(chatid, document=f"{temp}{filename}", caption=entry['title'])
                        except Exception as e:
                            logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
                else:
                    try:
                        await app.send_document(chatid, document=f"{temp}{filename}", caption=entry['title'])
                    except Exception as e:
                        logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

                os.remove(f"{temp}{filename}")

            else:
                print("Error al descargar la imagen.")


    rss_urls = get_feed_url()

    db = Mclient["rss"]


    while True:
        tasks = [asyncio.create_task(process_rss(url[0])) for url in rss_urls]

        await asyncio.gather(*tasks)
        #print(last_checked_time_g)
        await asyncio.sleep(300)