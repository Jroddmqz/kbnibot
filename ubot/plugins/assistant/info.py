from pyrogram import filters

from ubot import app, bot
from ubot.config import Config


@bot.on_message(filters.command(["info"], prefixes=[".","/"]) & filters.incoming)
async def info(client, message):
    if message.reply_to_message:
        username = message.reply_to_message.from_user.username
        id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        user_link = message.reply_to_message.from_user.mention

        if message.reply_to_message.from_user.photo:
            async for photo in app.get_chat_photos(message.reply_to_message.from_user.id,1):
                photo_ = await app.download_media((photo.file_id))
        else:
            photo_ = Config.img_url
    else:
        username = message.from_user.username
        id = message.from_user.id
        first_name = message.from_user.first_name
        user_link = message.from_user.mention

        if message.from_user.photo:
            async for photo in app.get_chat_photos(message.from_user.id,1):
                photo_ = await app.download_media(photo.file_id)
        else:
            photo_ = Config.img_url

    if username:
        username = f"@{username}"
        text = f"""
ID: <code>{id}</code>
Name: {user_link}
Username: {username}"""
    else:
        text = f"""
ID: <code>{id}</code>
First Name: {first_name}
User link: {user_link}"""
    await bot.send_document(message.chat.id, document=photo_, caption=text)
