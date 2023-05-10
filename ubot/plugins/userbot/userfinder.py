import asyncio
import logging
import random
import string

from pyrogram import filters

from ubot import app, bot, Mclient
from ubot.utils.misc import item_for_search


def eliminar_todos_duplicados():
    db = Mclient['users']
    collection = db['abandoned']
    pipeline = [
        {"$group": {
            "_id": {
                "chat_id": "$u_chat_id",
                "id": "$u_id",
                "user_status": "$u_user_status",
                "status": "$u_status"
            },
            "duplicados": {"$push": "$_id"},
            "total": {"$sum": 1}
        }},
        {"$match": {"total": {"$gt": 1}}}
    ]

    duplicados = []
    for doc in collection.aggregate(pipeline):
        duplicados.extend(doc["duplicados"])

    # Paso 2: eliminar documentos duplicados
    for dup_id in duplicados:
        collection.delete_one({"_id": dup_id})

    print(f"Se eliminaron {len(duplicados)} documentos duplicados.")

def consulta():
    db = Mclient['users']
    collection = db['abandoned']
    long_ago = []
    last_month = []

    result_long_ago = collection.find({"u_user_status": "UserStatus.LONG_AGO"})
    result_last_month = collection.find({"u_user_status": "UserStatus.LAST_MONTH"})

    for doc in result_long_ago:
        long_ago.append(doc["u_id"])

    for doc in result_last_month:
        last_month.append(doc["u_id"])
    return long_ago, last_month

def consulta_b(chat_id, type):
    db = Mclient['users']
    collection = db['abandoned']
    long_ago = []
    last_month = []

    if type == "all":
        result_long_ago = collection.find({"u_chat_id": chat_id, "u_user_status": "UserStatus.LONG_AGO"})
        result_last_month = collection.find({"u_chat_id": chat_id, "u_user_status": "UserStatus.LAST_MONTH"})
        for doc in result_long_ago:
            long_ago.append(doc["u_id"])

        for doc in result_last_month:
            last_month.append(doc["u_id"])
        return long_ago, last_month
    elif type == "long_ago":
        result_long_ago = collection.find({"u_chat_id": chat_id, "u_user_status": "UserStatus.LONG_AGO"})

        for doc in result_long_ago:
            long_ago.append(doc["u_id"])

        return long_ago, last_month

@bot.on_message(filters.command(["userfinder"], prefixes=[".","/"]) & filters.incoming)
async def userfinder(client, message):

    await message.reply_text("Esto puede tomar algunos minutos")

    db = Mclient["users"]
    collection = db['abandoned']
    regis = db['registro']

    chat_id_ = -1001334411290 #neko6music
    #chat_id_ = -1001389978121 #lewdusers

    combi = item_for_search()
    #combi = ["v4", "v5"]
    for x in combi:
        x_query_ = "".join([x[0] for palabra in x.split()])
        print(f"Query:{x_query_} - {x}")
        async for member in bot.get_chat_members(chat_id_, query=x):
            if member.user.first_name is None:
                member_user_first_name = str(member.user.first_name).replace(" ", "")
                txt_ = f"{chat_id_} {member.user.id} {member_user_first_name} {member.user.username} {member.user.status} {member.status}"
                u_chat_id, u_id, u_first_name, u_username, u_user_status, u_status = txt_.split(" ")
                print(txt_)
                item = {"u_chat_id": u_chat_id, "u_id": u_id, "u_first_name": u_first_name, "u_username": u_username, "u_user_status": u_user_status, "u_status": u_status}
                collection.insert_one(item)
            if str(member.user.status) in ["UserStatus.LONG_AGO","UserStatus.LAST_MONTH"]:
                member_user_first_name = str(member.user.first_name).replace(" ", "")
                txt_ = f"{chat_id_} {member.user.id} {member_user_first_name} {member.user.username} {member.user.status} {member.status}"
                u_chat_id, u_id, u_first_name, u_username, u_user_status, u_status = txt_.split(" ")
                print(txt_)
                item = {"u_chat_id": u_chat_id, "u_id": u_id, "u_first_name": u_first_name, "u_username": u_username, "u_user_status": u_user_status, "u_status": u_status}
                collection.insert_one(item)

    eliminar_todos_duplicados()
    long_ago, last_month = consulta()
    print(f"hay {int(len(long_ago) + int(len(last_month)))} cuentas abandonadas:")
    print(f"{len(long_ago)} con status UserStatus.LONG_AGO\n{len(last_month)} con status UserStatus.LAST_MONTH")

    _type_ = "all"
    key_search = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(5))
    my_search = {"key_search": key_search, "chat_id_": chat_id_, "_type_": _type_}
    print(f"Si desea kickear a todas ejecute: .delete {key_search}")  # all
    regis.insert_one(my_search)

    _type_ = "long_ago"
    key_search = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(5))
    my_search = {"key_search": key_search, "chat_id_": chat_id_, "_type_": _type_}
    print(f"Si desea kickear solo LONG_AGO: .delete {key_search}") #long_ago
    regis.insert_one(my_search)





@bot.on_message(filters.command(["delete"], prefixes=[".", "/"]) & filters.incoming)
async def delete(client, message):
    try:
        token = message.command[1]
    except:
        print("error de comando")
        return

    db = Mclient["users"]
    regis = db['registro']

    my_search = regis.find({"key_search": f"{token}"})
    for item in my_search:
        to_del_token = item["key_search"]
        to_del_chat_id = item["chat_id_"]
        to_del_type = item["_type_"]
        print(f"{to_del_chat_id} + {to_del_type}")
    try:
        if token == to_del_token:
            print("comando  valido")
    except:
        print("token invalido")
        return
    a, b = consulta_b(str(to_del_chat_id), to_del_type)

    for x in a:
        try:
            print(f"Chat id:{to_del_chat_id} id user: {x}")
            await app.ban_chat_member(chat_id=to_del_chat_id, user_id=x)
            await asyncio.sleep(1)
        except Exception as e:
            logging.error("[KBNIBOT] - Failed To ban : " + f" - {str(e)}")
    for x in b:
        try:
            print(f"Chat id:{to_del_chat_id} id user: {x}")
            await app.ban_chat_member(chat_id= to_del_chat_id, user_id = x)
            await asyncio.sleep(1)
        except Exception as e:
            logging.error("[KBNIBOT] - Failed To ban : " + f" - {str(e)}")


@bot.on_message(filters.command(["ejecutar"], prefixes=[".", "/"]) & filters.incoming)
async def ejecutar(client, message):
    print(message)
    db = Mclient['users']
    collection = db['commands_record']
    #eliminar_todos_duplicados()
    #long_ago, last_month = consulta()
    #print(f"hay {int(len(long_ago)+int(len(last_month)))} cuentas abandonadas:")
    #print(f"{len(long_ago)} con status UserStatus.LONG_AGO\n{len(last_month)} con status UserStatus.LAST_MONTH")
    #print("finalizado")
