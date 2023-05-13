# -*- encoding: utf-8 -*-
"""Config vars module"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    api_id = int(os.environ.get('API_ID'))
    api_hash = os.environ.get('API_HASH', None)
    bot_token = os.environ.get('BOT_TOKEN', None)
    bot_token2 = os.environ.get('BOT_TOKEN2', None)

    document_root = os.environ.get('DOCUMENT_ROOT')
    log_group = int(os.environ.get('LOG_GROUP', False))
    img_url = os.environ.get('IMG_URL', None)

    interval = int(os.environ.get('INTERVAL'))
    start_date = os.environ.get('START_DATE')
    caption = os.environ.get('CAPTION')

    mongodb = os.environ.get('MONGODB')
