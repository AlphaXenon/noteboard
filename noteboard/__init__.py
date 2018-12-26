import os

# Paths
DIR_PATH = os.path.join(os.path.expanduser("~"), ".noteboard/")
CONFIG_PATH = os.path.join(DIR_PATH, "config.ini")
LOG_PATH = os.path.join(DIR_PATH, "noteboard.log")
STATES_PATH = os.path.join(DIR_PATH, "states.pkl")
STORAGE_PATH = os.path.join(DIR_PATH, "storage")
if not os.path.isdir(DIR_PATH):
    os.mkdir(DIR_PATH)

# Config
from .config import init_config, load_config

if not os.path.isfile(CONFIG_PATH):
    init_config()
CONFIG = load_config()
DEFAULTS = CONFIG["DEFAULTS"]
COLORS = CONFIG["COLORS"]

from .storage import Storage
