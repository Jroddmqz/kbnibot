import datetime
import os

from pyrogram import filters, enums
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

from ubot import app, bot
from ubot.config import Config
from ubot.utils.misc import progress, get_file_size_in_mb, file_list, resizer, thumbail_


@app.on_message(filters.command(["ufd"], prefixes=[".","/"]) & filters.me)
async def ufd(client, message):
    # Config.chat_id is now message.chat.id
    await app.send_message(message.chat.id, "hi ufd:D")
    await message.reply_text("XDD")

    filename = sorted(list(file_list(Config.document_root, set())))

    if Config.start_date:
        schedule = datetime.datetime.strptime(Config.start_date, '%Y-%m-%d %H:%M:%S')
    else:
        schedule = datetime.datetime.now()

    counter = len(filename)
    curr = 0
    in_exe = False
    n_file = []
    n_file_raw = []
    finaldel = []

    order_by_extension = ['jpg', 'jpeg', 'png']
    keys = {k: v for v, k in enumerate(order_by_extension)}
    filename = sorted(filename, key=lambda y: keys.get(str(y).split('.')[1], float('inf')))

    for x in filename:
        if not in_exe:
            if Config.interval != 0:
                schedule = schedule + datetime.timedelta(minutes=Config.interval)
            else:
                schedule = schedule + datetime.timedelta(seconds=60)

        curr += 1
        start_date = datetime.datetime.now()
        size = get_file_size_in_mb(x)
        print(str(curr) + '/' + str(counter) + ' [' + datetime.datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S") + '][' + str(size) + 'MB] Uploading ' + x + ' at ' + str(schedule))
        extension = x.split('.')[-1]

        try:
            n_extension = filename[curr].split('.')[-1]
        except IndexError:
            n_extension = None
        if extension.lower() in {'jpg', 'png', 'jpeg'}:
            x_resize = resizer(x)
            finaldel.append(x_resize)
            if n_extension == extension and len(n_file) <= 8:
                if len(n_file) == 0:
                    n_file.append(InputMediaPhoto(x_resize, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                    n_file_raw.append(InputMediaDocument(x, parse_mode=enums.ParseMode.HTML))
                else:
                    n_file.append(InputMediaPhoto(x_resize))
                    n_file_raw.append(InputMediaDocument(x))
                in_exe = True
            else:
                if len(n_file) > 0:
                    n_file.append(InputMediaPhoto(x_resize))
                    n_file_raw.append(InputMediaDocument(x))
                    await app.send_media_group(
                        chat_id=int(message.chat.id),
                        media=n_file,
                        schedule_date=schedule
                    )
                    await app.send_media_group(
                        chat_id=int(message.chat.id),
                        media=n_file_raw,
                        schedule_date=schedule
                    )
                    n_file = []
                    n_file_raw = []
                else:
                    await app.send_photo(
                        chat_id=int(message.chat.id),
                        photo=x_resize,
                        schedule_date=schedule,
                        caption=Config.caption,
                        parse_mode=enums.ParseMode.HTML
                    )
                    await app.send_document(
                        chat_id=int(message.chat.id),
                        document=x,
                        schedule_date=schedule,
                        parse_mode=enums.ParseMode.HTML
                    )
        elif extension.lower() in {'mp4', 'mkv', 'avi', 'mov'}:
            _thumbs_ = thumbail_(x)
            finaldel.append(_thumbs_)
            if _thumbs_ is None:
                print(f"pass video corrupted:{x}")
                continue
                path_, ext_ = os.path.splitext(x)
                x = path_ + ".mp4"

            if n_extension == extension and len(n_file) <= 8:
                if len(n_file) == 0:
                    n_file.append(
                        InputMediaVideo(x, thumb=_thumbs_, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                else:
                    n_file.append(InputMediaVideo(x, thumb=_thumbs_))
                in_exe = True
            else:
                if len(n_file) > 0:
                    n_file.append(InputMediaVideo(x, thumb=_thumbs_))
                    await app.send_media_group(chat_id=int(message.chat.id), media=n_file, schedule_date=schedule)
                    n_file = []
                else:
                    await app.send_video(
                        chat_id=int(message.chat.id),
                        video=x,
                        thumb=_thumbs_,
                        schedule_date=schedule,
                        caption=Config.caption,
                        progress=progress,
                        parse_mode=enums.ParseMode.HTML
                    )
        else:
            if n_extension == extension and len(n_file) <= 8:
                if len(n_file) == 0:
                    n_file.append(InputMediaDocument(x, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                else:
                    n_file.append(InputMediaDocument(x))
                in_exe = True
            else:
                if len(n_file) > 0:
                    n_file.append(InputMediaDocument(x))
                    await app.send_media_group(
                        chat_id=int(message.chat.id),
                        media=n_file,
                        schedule_date=schedule
                    )
                    n_file = []
                else:
                    await app.send_document(
                        chat_id=int(message.chat.id),
                        document=x,
                        schedule_date=schedule,
                        caption=Config.caption,
                        progress=progress,
                        parse_mode=enums.ParseMode.HTML
                    )

        if not in_exe:
            difference = datetime.datetime.now() - start_date
            if difference.total_seconds() != 0:
                speed = round(size / round(difference.total_seconds(), 4), 2)
            else:
                speed = 1

            print("\r", 'Finished: ' + x
                  + '. Size: ' + str(size)
                  + 'MB ' + str(round(difference.total_seconds(), 4)) + 's at '
                  + str(speed) + ' MB/s')
            in_exe = False

    for x in finaldel:
        if os.path.exists(x):
            os.remove(x)
    finaldel.clear()