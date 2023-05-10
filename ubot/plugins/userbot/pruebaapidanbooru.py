import time, feedparser
import urllib.parse

from dateutil.parser import parse
from ubot.utils.san import Bruteforce
import requests, os
from datetime import datetime

def get_feed_entries(url):
    entries = []
    feed = feedparser.parse(url)
    if feed['feed']['title'] in 'Danbooru: order:rank':
        order_rank = "rank"
    else:
        order_rank = ""

    for entry in feed.entries:
        #print(entry)
        entry_data = {
            "title": entry.title,
            "link": entry.link,
            "updated": entry.updated,
            "updated_parsed": entry.updated_parsed,
            "author": entry.author,
            "order_rank": order_rank,
        }
        entries.append(entry_data)
    return entries

def get_recent_entries(url, last_checked_time=None):
    entries = get_feed_entries(url)
    recent_entries = []
    current_time = time.time()
    if last_checked_time is None:
        last_checked_time = current_time
    for entry_ in entries:
        #print(entry_)
        published_time = parse(entry_["updated"]).timestamp()
        if last_checked_time < published_time <= current_time:
            print("agregando")
            recent_entries.append(entry_)
    return recent_entries, current_time

def get_feed_url():
    url = []
    #url.append(["https://danbooru.donmai.us/posts.atom", "@danboruu channel"])
    url.append(["https://siftrss.com/f/9Mn0Rq9QgG", "loliboru channel"])
    return url

last_checked_time = time.time()
entries, last_checked_time = get_recent_entries("https://siftrss.com/f/9Mn0Rq9QgG", last_checked_time)
#last_checked_time = time.time()
#url = get_feed_url()
#for x in url:

#    print(len(x[0]))
#    entries, last_checked_time = get_recent_entries(x[0], last_checked_time)

#temp = '.temp/'
#b = Bruteforce()
#archive = b.booru("https://lolibooru.moe/post/show/565564", site="lolibooru")
##archive = urllib.parse.quote(archive, safe="")
#archive = archive.replace(" ", "%20")

#print(archive)
#response = requests.get(archive)
#print(response)
#if response.status_code == 200:
#    path_, ext_ = os.path.splitext(archive)
#    now = datetime.now()
#    date_time = now.strftime("%Y%m%d_%H%M%S")
#    with open(f"{date_time}{ext_}", "wb") as f:
#        f.write(response.content)