import os
import time
import cv2
import logging
import imageio
import asyncio
import pathlib
import itertools
from PIL import Image
from ubot import app, bot, Mclient, log_group
from moviepy.video.io.VideoFileClip import VideoFileClip



def item_for_search():
    let_ = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    num_ = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

    # Crear todas las combinaciones posibles de profundidad 2
    comb_ = itertools.product(let_ + num_, repeat=2)

    # Ordenar las combinaciones alfanuméricamente
    ordencomb_ = sorted([''.join(combi) for combi in comb_])
    return ordencomb_


def progress(current, total):
    percent = 100 * (current / total)
    bar_length = 35
    filled_length = int(percent / 100 * bar_length)
    bar = '▋' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r[{bar}] {round(percent, 2)}%', end='')


def get_file_size_in_mb(file_path):
    stat_info = os.stat(file_path)
    size = stat_info.st_size / 1024 / 1024
    return int(round(size, 2))


def file_list(path, sett):
    pathlib.Path(path)
    for filepath in pathlib.Path(path).glob("**/*"):
        if os.path.isdir(filepath):
            file_list(filepath, sett)
        else:
            sett.add(str(filepath.parent) + "/" + str(filepath.name))
    return sett


def resizer(_image_):
    with Image.open(_image_) as img:
        width, height = img.size
        img = img.convert("RGB")

    if width * height > 5242880 or width > 4096 or height > 4096:
        new_width, new_height = width, height
        while new_width * new_height > 5242880 or new_width > 4096 or new_height > 4096:
            new_width = int(new_width * 0.9)
            new_height = int(new_height * 0.9)

        resized_img = img.resize((new_width, new_height))
    else:
        resized_img = img

    path_, ext_ = os.path.splitext(_image_)
    newname = path_ + "lite" + ext_
    resized_img.save(newname)
    return newname


def thumbail_(_video_):
    path_, ext_ = os.path.splitext(_video_)
    namethumb = path_ + ".jpg"
    if ext_.lower() == ".mp4":
        # Abrir el video
        cap = cv2.VideoCapture(_video_)
        # Obtener el número de fotogramas
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Establecer el fotograma alrededor del cual queremos tomar la miniatura
        frame_to_capture = int(total_frames / 3)
        # Establecer la posición del fotograma
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_capture)
        # Leer el fotograma
        ret, frame = cap.read()
        # Guardar la miniatura como imagen
        cv2.imwrite(namethumb, frame)
        # Liberar los recursos
        cap.release()
    elif ext_.lower() == ".mkv":
        # Abrir el archivo MKV
        video = VideoFileClip(_video_)
        # Obtener la miniatura en el segundo 5 del video
        thumbnail = video.get_frame(20)
        # Guardar la miniatura como imagen
        imageio.imwrite(namethumb, thumbnail)
        # Liberar los recursos
        video.close()
    elif ext_.lower() == ".mov":
        # Abrir el archivo MOV
        try:
            video = VideoFileClip(_video_)
            # Obtener la miniatura en el segundo 5 del video
            thumbnail = video.get_frame(5)
            # Guardar la miniatura como imagen
            # thumbnail.save_frame(newname)
            # np.savetxt('thumbnail.jpg', thumbnail)
            imageio.imwrite(namethumb, thumbnail)
            video.write_videofile(path_ + ".mp4")
            # Liberar los recursos
            video.close()
            print("El archivo MOV parece estar bien.")
        except:
            print("El archivo MOV parece estar dañado.")
            return None
    return namethumb


async def is_chat(client, item):
    try:
        chat_id = int(item)
        try:
            chat = await client.get_chat(chat_id)
        except:
            return None
        chat_id = chat.id
    except ValueError:
        if not item.startswith("@"):
            return None
        try:
            chat = await client.get_chat(item)
        except:
            return None
        chat_id = chat.id
    return chat_id


async def upload_file(client, file_path, chat_id, capy, ext_, x_item=False):
    _sent_ = None
    try:
        if ext_.lower() in {'.jpg', '.png', '.webp', '.jpeg'}:
            new_file = resizer(file_path)
            try:
                _sent_ = await client.send_photo(chat_id, photo=new_file, caption=str(capy))
                await asyncio.sleep(1)
                await client.send_document(chat_id, document=file_path)
            except:
                try:
                    _sent_ = await client.send_document(chat_id, document=file_path, caption=str(capy))
                except Exception as e:
                    logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
            if os.path.exists(new_file):
                os.remove(new_file)
        elif ext_.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
            try:
                _sent_ = await client.send_video(chat_id, video=file_path, caption=str(capy))
                await asyncio.sleep(1)
            except:
                try:
                    _sent_ = await client.send_document(chat_id, document=file_path, caption=str(capy))
                except Exception as e:
                    logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")
        else:
            try:
                _sent_ = await client.send_document(chat_id, document=file_path, caption=str(capy))
            except Exception as e:
                logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

        os.remove(file_path)

        if x_item is None:
            pass
        else:
            db = Mclient["rule"]
            collect = db[f"{x_item['tag']}"]
            if _sent_ is not None:
                if not x_item['published']:
                    fil_ter = {'id': x_item['id']}
                    update = {'$set': {'published': True}}
                    collect.update_one(fil_ter, update)
    except Exception as e:
        if "[420 FLOOD_WAIT_X]" in str(e):
            print(f"str(e)-{str(e)}-")
            print('Flood: Wait for', int(str(e).split()[5]), 'seconds')
            time.sleep(int(str(e).split()[5]))
        else:
            logging.error("[KBNIBOT] - Failed: " + f"{str(e)}")

async def upload_from_queue(queue):
    while True:
        if not queue.empty():
            task = await queue.get()
            client, file_path, chat_id, capy, ext_, x = task
            await upload_file(client, file_path, chat_id, capy, ext_, x)
            queue.task_done()
        await asyncio.sleep(1)
