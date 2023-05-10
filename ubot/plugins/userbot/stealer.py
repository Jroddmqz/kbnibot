import asyncio
import os

from pymongo import ASCENDING, DESCENDING
from pyrogram import filters
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from ubot.utils.misc import progress
from ubot import app, bot, Mclient
import logging


# AUN NO FUNCIONA


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


@app.on_message(filters.command(["steal"], prefixes=[".", "/"]) & filters.me)
async def steal(client, message):
    if len(message.command) == 1:  # .steal
        print(f"mensaaje sin parametros")
        return

    def is_int(item):
        try:
            msg_id = int(item)
            return msg_id
        except:
            return None

    steal_ = ""
    origin_ = ""
    destiny_ = ""
    msg_ = ""

    if message.reply_to_message:
        origin_ = message.chat.id
        try:
            steal_, destiny_ = message.command  # .steal @destiny
        except:
            print("solo se permiten 2 parametros eg. .steal @destino")
            return
        msg_ = message.reply_to_message_id

        if message.reply_to_message.forward_from_chat:
            origin_ = message.reply_to_message.forward_from_chat.id
            try:
                steal_, destiny_ = message.command  # .steal @destiny
            except:
                print("solo se permiten 2 parametros eg. .steal @destino")
                return
            msg_ = message.reply_to_message.forward_from_message_id

    if not message.reply_to_message:
        try:
            # .steal @origen @destino @msg
            val1, val2, val3, val4 = message.command
            print("case 4")
            origin_ = await is_chat(val2)
            destiny_ = await is_chat(val3)
            msg_ = is_int(val4)
        except:
            try:
                # .steal @origen @destino
                # .steal @destino @msg
                val1, val2, val3 = message.command
                if (await is_chat(val2)) is not None and (await is_chat(val3)) is not None:
                    print("case 3a")
                    origin_ = await is_chat(val2)
                    destiny_ = await is_chat(val3)
                    msg_ = 0
                elif (await is_chat(val2)) is not None or is_int(val3) is not None:
                    print("case 3b")
                    origin_ = message.chat.id
                    destiny_ = await is_chat(val2)
                    msg_ = is_int(val3)
                else:
                    print("revisa tus parametros, canales no validos")
            except:
                try:
                    print("case 2")
                    # .steal @destino
                    val1, val2 = message.command
                    origin_ = message.chat.id
                    destiny_ = await is_chat(val2)
                    if destiny_ == None:
                        print("canal no valido")
                    msg_ = 0
                except:
                    print("error de parametros")
                    return

    print("----")
    print(origin_)
    print(destiny_)
    print(msg_)
    print("----")

    if origin_ is None or destiny_ is None or msg_ is None:
        if origin_ is None:
            print("Origen no válido")
        elif destiny_ is None:
            print("Destino no válido")
        else:
            print("Mensaje no válido")
        return
    chat = await app.get_chat(origin_)

    db = Mclient["chats"]
    collection = db[f'{chat.title}']
    order = 0
    async for message in app.get_chat_history(origin_, offset_id=msg_):
        try:
            if message.media:
                txt = f"{message.chat.id} {message.id} {message.media_group_id} {message.media} {message.chat.has_protected_content}"
                _chatid, _messageid, _mediagroupid, _media, _hasprotected = txt.split(" ")
                _caption = str(message.caption)
                item = {"chatid": _chatid, "messageid": _messageid, "mediagroupid": _mediagroupid, "mediatype": _media, "hasprotected": _hasprotected, "caption": _caption}
                collection.insert_one(item)
                print(item)
        except Exception as e:
            logging.error("[KBNIBOT] - Failed To Error : " + f"{str(e)}")

    items = collection.find().sort([("$natural", DESCENDING)])

    medgrpid = ""
    group = []
    groupy = []
    capy = ""
    for x in items:
        if str(x['mediagroupid']) == "None":
            try:
                if x['caption'] == "None":
                    capy = ""
                await app.copy_message(destiny_, from_chat_id=x['chatid'], message_id=int(x['messageid']), caption=capy)
                print(f"Enviado individual: https://t.me/c/1578030979/{x['messageid']}" )
                await asyncio.sleep(1)
            except:
                try:
                    one = await app.get_messages(x['chatid'], int(x['messageid']))
                    file = await app.download_media(one, progress=progress)
                    if one.photo:
                        await app.send_photo(destiny_, photo=file, caption=one.caption)
                    if one.video:
                        await app.send_video(destiny_, video=file, caption=one.caption)
                    if one.document:
                        await app.send_document(destiny_, document=file, caption=one.caption)
                    os.remove(file)
                    print(f"Enviado individual caso 2: https://t.me/c/1578030979/{x['messageid']}")
                    await asyncio.sleep(1)

                except Exception as e:
                    logging.error("[USER] - Failed : " + f"- {str(e)}")
        elif str(x['mediagroupid']) != "None":
            if medgrpid == "":
                medgrpid = x['mediagroupid']

                group = await app.get_media_group(x['chatid'], message_id=int(x['messageid']))

                for m_s_g in group:
                    if m_s_g.caption:
                        capy = m_s_g.caption

                    if x['mediatype'] == 'MessageMediaType.PHOTO':
                        groupy.append(InputMediaPhoto(m_s_g.photo.file_id, caption=capy))
                    elif x['mediatype'] == 'MessageMediaType.VIDEO':
                        groupy.append(InputMediaVideo(m_s_g.video.file_id, caption=capy))
                    elif x['mediatype'] == 'MessageMediaType.DOCUMENT':
                        groupy.append(InputMediaDocument(m_s_g.document.file_id, caption=capy))
                    capy = ""
                try:
                    await app.send_media_group(destiny_, media=groupy)
                    print(f"Enviado grupal caso 1: https://t.me/c/1578030979/{x['messageid']}")
                    await asyncio.sleep(1)

                except Exception as e:
                    logging.error("[USER] - Failed : " + f"- {str(e)}")

                await asyncio.sleep(1)
                group.clear()
                groupy.clear()
            else:
                if medgrpid != x['mediagroupid']:

                    group = await app.get_media_group(x['chatid'], message_id=int(x['messageid']))

                    for m_s_g in group:
                        if m_s_g.caption:
                            capy = m_s_g.caption

                        if x['mediatype'] == 'MessageMediaType.PHOTO':
                            groupy.append(InputMediaPhoto(m_s_g.photo.file_id, caption=capy))
                        elif x['mediatype'] == 'MessageMediaType.VIDEO':
                            groupy.append(InputMediaVideo(m_s_g.video.file_id, caption=capy))
                        elif x['mediatype'] == 'MessageMediaType.DOCUMENT':
                            groupy.append(InputMediaDocument(m_s_g.document.file_id, caption=capy))
                        capy = ""
                    try:
                        await app.send_media_group(destiny_, media=groupy)
                        print(f"Enviado grupal caso 2: https://t.me/c/1578030979/{x['messageid']}")
                        await asyncio.sleep(1)

                    except Exception as e:
                        logging.error("[USER] - Failed : " + f"- {str(e)}")

                    print("enviando case 2")
                    await asyncio.sleep(1)
                    group.clear()
                    groupy.clear()
                    medgrpid = x['mediagroupid']
                elif medgrpid == x['mediagroupid']:
                    print("pasando")
                    pass


    collection.drop()


@app.on_message(filters.command(["cont"], prefixes=[".", "/"]) & filters.me)
async def cont(client, message):
    print("ejecutando cont")
    if len(message.command) == 1:  # .steal
        print(f"mensaaje sin parametros")
        return

    def is_int(item):
        try:
            msg_id = int(item)
            return msg_id
        except:
            return None

    steal_ = ""
    origin_ = ""
    destiny_ = ""
    msg_ = ""

    if message.reply_to_message:
        origin_ = message.chat.id
        try:
            steal_, destiny_ = message.command  # .steal @destiny
        except:
            print("solo se permiten 2 parametros eg. .steal @destino")
            return
        msg_ = message.reply_to_message_id

        if message.reply_to_message.forward_from_chat:
            origin_ = message.reply_to_message.forward_from_chat.id
            try:
                steal_, destiny_ = message.command  # .steal @destiny
            except:
                print("solo se permiten 2 parametros eg. .steal @destino")
                return
            msg_ = message.reply_to_message.forward_from_message_id

    if not message.reply_to_message:
        try:
            # .steal @origen @destino @msg
            val1, val2, val3, val4 = message.command
            print("case 4")
            origin_ = await is_chat(val2)
            destiny_ = await is_chat(val3)
            msg_ = is_int(val4)
        except:
            try:
                # .steal @origen @destino
                # .steal @destino @msg
                val1, val2, val3 = message.command
                if (await is_chat(val2)) is not None and (await is_chat(val3)) is not None:
                    print("case 3a")
                    origin_ = await is_chat(val2)
                    destiny_ = await is_chat(val3)
                    msg_ = 0
                elif (await is_chat(val2)) is not None or is_int(val3) is not None:
                    print("case 3b")
                    origin_ = message.chat.id
                    destiny_ = await is_chat(val2)
                    msg_ = is_int(val3)
                else:
                    print("revisa tus parametros, canales no validos")
            except:
                try:
                    print("case 2")
                    # .steal @destino
                    val1, val2 = message.command
                    origin_ = message.chat.id
                    destiny_ = await is_chat(val2)
                    if destiny_ == None:
                        print("canal no valido")
                    msg_ = 0
                except:
                    print("error de parametros")
                    return

    print("----")
    print(origin_)
    print(destiny_)
    print(msg_)
    print("----")

    if origin_ is None or destiny_ is None or msg_ is None:
        if origin_ is None:
            print("Origen no válido")
        elif destiny_ is None:
            print("Destino no válido")
        else:
            print("Mensaje no válido")
        return
    chat = await app.get_chat(origin_)

    db = Mclient["chats"]
    collection = db[f'{chat.title}']

    items = collection.find().sort([("$natural", DESCENDING)])

    medgrpid = ""
    group = []
    groupy = []
    capy = ""
    for x in items:
        if str(x['mediagroupid']) == "None":
            try:
                if x['caption'] == "None":
                    capy = ""
                await app.copy_message(destiny_, from_chat_id=x['chatid'], message_id=int(x['messageid']), caption=capy)
                print(f"Enviado individual: https://t.me/c/1578030979/{x['messageid']}" )
                await asyncio.sleep(1)
            except:
                try:
                    one = await app.get_messages(x['chatid'], int(x['messageid']))
                    file = await app.download_media(one, progress=progress)
                    if one.photo:
                        await app.send_photo(destiny_, photo=file, caption=one.caption)
                    if one.video:
                        await app.send_video(destiny_, video=file, caption=one.caption)
                    if one.document:
                        await app.send_document(destiny_, document=file, caption=one.caption)
                    os.remove(file)
                    print(f"Enviado individual caso 2: https://t.me/c/1578030979/{x['messageid']}")
                    await asyncio.sleep(1)

                except Exception as e:
                    logging.error("[USER] - Failed : " + f"- {str(e)}")
        elif str(x['mediagroupid']) != "None":
            if medgrpid == "":
                medgrpid = x['mediagroupid']

                group = await app.get_media_group(x['chatid'], message_id=int(x['messageid']))

                for m_s_g in group:
                    if m_s_g.caption:
                        capy = m_s_g.caption

                    if x['mediatype'] == 'MessageMediaType.PHOTO':
                        groupy.append(InputMediaPhoto(m_s_g.photo.file_id, caption=capy))
                    elif x['mediatype'] == 'MessageMediaType.VIDEO':
                        groupy.append(InputMediaVideo(m_s_g.video.file_id, caption=capy))
                    elif x['mediatype'] == 'MessageMediaType.DOCUMENT':
                        groupy.append(InputMediaDocument(m_s_g.document.file_id, caption=capy))
                    capy = ""
                try:
                    await app.send_media_group(destiny_, media=groupy)
                    print(f"Enviado grupal caso 1: https://t.me/c/1578030979/{x['messageid']}")
                    await asyncio.sleep(1)

                except Exception as e:
                    logging.error("[USER] - Failed : " + f"- {str(e)}")

                await asyncio.sleep(1)
                group.clear()
                groupy.clear()
            else:
                if medgrpid != x['mediagroupid']:

                    group = await app.get_media_group(x['chatid'], message_id=int(x['messageid']))

                    for m_s_g in group:
                        if m_s_g.caption:
                            capy = m_s_g.caption

                        if x['mediatype'] == 'MessageMediaType.PHOTO':
                            groupy.append(InputMediaPhoto(m_s_g.photo.file_id, caption=capy))
                        elif x['mediatype'] == 'MessageMediaType.VIDEO':
                            groupy.append(InputMediaVideo(m_s_g.video.file_id, caption=capy))
                        elif x['mediatype'] == 'MessageMediaType.DOCUMENT':
                            groupy.append(InputMediaDocument(m_s_g.document.file_id, caption=capy))
                        capy = ""
                    try:
                        await app.send_media_group(destiny_, media=groupy)
                        print(f"Enviado grupal caso 2: https://t.me/c/1578030979/{x['messageid']}")
                        await asyncio.sleep(1)

                    except Exception as e:
                        logging.error("[USER] - Failed : " + f"- {str(e)}")

                    print("enviando case 2")
                    await asyncio.sleep(1)
                    group.clear()
                    groupy.clear()
                    medgrpid = x['mediagroupid']
                elif medgrpid == x['mediagroupid']:
                    print("pasando")
                    pass

    collection.drop()