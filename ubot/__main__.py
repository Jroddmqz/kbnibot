import logging
import os
import pyrogram

# from config import Config
# from ubot.utils.misc import item_for_search
from ubot import app, bot, bot2
from ubot.utils.startup_helper import plugin_collecter, load_plugin


async def run():
    ruta_actual = os.getcwd()
    print(ruta_actual)
    if bot:
        await bot.start()
        bot.me = await bot.get_me()
        assistant_mods = plugin_collecter("./ubot/plugins/assistant/")
        for mods in assistant_mods:
            try:
                load_plugin(mods, assistant=True)
            except Exception as e:
                logging.error("[ASSISTANT] - Failed To Load : " + f"{mods} - {str(e)}")
    if bot2:
        await bot2.start()
        bot2.me = await bot2.get_me()
    await app.start()
    userbot_mods = plugin_collecter("./ubot/plugins/userbot/")
    for mods in userbot_mods:
        try:
            load_plugin(mods)
        except Exception as e:
            logging.error("[KBNIBOT] - Failed To Load : " + f"{mods} - {str(e)}")

    await pyrogram.idle()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.loop.run_until_complete(run())
