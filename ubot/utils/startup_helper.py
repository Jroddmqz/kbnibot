import glob
import importlib
import logging
import ntpath


def load_plugin(plugin_name, assistant=False):
    """Load PLugins - Assitant & User Using ImportLib"""
    if plugin_name.endswith("__"):
        pass
    else:
        if assistant:
            plugin_path = "ubot.plugins.assistant." + plugin_name
        else:
            plugin_path = "ubot.plugins.userbot." + plugin_name
        loader_type = "[Assistant]" if assistant else "[User]"
        importlib.import_module(plugin_path)
        logging.info(f"{loader_type} - Loaded : " + str(plugin_name))


def plugin_collecter(path):
    """Collects All Files In A Path And Give Its Name"""
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        pathe = path + "*.py"
    else:
        pathe = path + "/*.py"
    Poppy = glob.glob(pathe)
    final = []
    Pop = Poppy
    for x in Pop:
        k = ntpath.basename(x)
        if k.endswith(".py"):
            lily = k.replace(".py", "")
            final.append(lily)
    return final