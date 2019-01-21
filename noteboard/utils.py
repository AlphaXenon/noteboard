import time
import datetime
import os
import json


DEFAULT = {
    "StoragePath": "~/.noteboard/",
    "DefaultBoardName": "Board",
}


def get_time():
    date = datetime.date.today().strftime("%a %d %b %Y")
    timestamp = int(time.time())
    return date, timestamp


def init_config(path):
    """Initialise configurations file. If file already exists, it will be overwritten."""
    with open(path, "w+") as f:
        json.dump(DEFAULT, f, sort_keys=True, indent=4)


def load_config(path):
    """Load configurations file. If file does not exist, call `init_config()`."""
    if not os.path.isfile(path):
        init_config(path)

    with open(path, "r+") as f:
        config = json.load(f)
    return config
