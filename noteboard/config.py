import os
import configparser

from . import CONFIG_PATH


def init_config():
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    config["DEFAULTS"] = {
        "; default board if no board is specified when adding items": None,
        "board": "Board"
    }
    config["COLORS"] = {
        "; Default colors of each actions.": None,
        "; Values must be valid properties of colorama.Fore": None,
        "; Values must be in upper cases.": None,
        "run": "LIGHTCYAN_EX",
        "add": "GREEN",
        "remove": "MAGENTA",
        "clear": "RED",
        "tick": "LIGHTYELLOW_EX",
        "mark": "CYAN",
        "star": "YELLOW",
        "edit": "BLUE",
        "tag": "LIGHTBLUE_EX",
        "import": "",
        "export": "",
        "undo": "BLUE",
        "reset": "YELLOW"
    }
    with open(CONFIG_PATH, "w+") as f:
        config.write(f)


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config
