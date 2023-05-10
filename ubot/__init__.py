import logging

from pymongo import MongoClient
from pyrogram import Client

from .config import Config

# Enable Logging For Pyrogram
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [kbnibot] - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("apscheduler").setLevel(logging.ERROR)

if not Config.api_id:
    logging.error("No Api-ID Found! Exiting!")
    quit(1)

if not Config.api_hash:
    logging.error("No ApiHash Found! Exiting!")
    quit(1)

if not Config.log_group:
    logging.error("No Log Group ID Found! Exiting!")
    quit(1)

if not Config.bot_token:
    logging.error("No bot_token Found! Exiting!")
    quit(1)


if not Config.img_url:
    Config.img_url = "https://telegra.ph/file/d774d2684f524d7ae6ec1.png"


app = Client(
    "kbnibot",
    api_id=Config.api_id, api_hash=Config.api_hash,
)

if Config.bot_token:
    bot = Client(
        "assistant",
        api_id=Config.api_id,
        api_hash=Config.api_hash,
        bot_token=Config.bot_token,
        sleep_threshold=180,
    )
else:
    bot = None

Mclient = MongoClient(Config.mongodb)
