# Prepare directory paths
import os

from .utils import init_config, load_config


CONFIG_DIR_PATH = os.path.join(os.path.expanduser("~"), ".config/", "noteboard/")
CONFIG_PATH = os.path.join(CONFIG_DIR_PATH, "config.json")

if not os.path.isdir(os.path.join(os.path.expanduser("~"), ".config/")):
    os.mkdir(os.path.join(os.path.expanduser("~"), ".config/"))
if not os.path.isdir(CONFIG_DIR_PATH):
    os.mkdir(CONFIG_DIR_PATH)
if not os.path.isfile(CONFIG_PATH):
    init_config(CONFIG_PATH)


DIR_PATH = os.path.join(os.path.expanduser("~"), ".noteboard/")
config = load_config(CONFIG_PATH)

path = config.get("StoragePath") or DIR_PATH
path = os.path.expanduser(path)
if not os.path.isdir(path):
    os.mkdir(path)

LOG_PATH = os.path.join(path, "noteboard.log")
STATES_PATH = os.path.join(path, "states.pkl.gz")
STORAGE_PATH = os.path.join(path, "storage")
STORAGE_GZ_PATH = os.path.join(path, "storage.gz")

DEFAULT_BOARD = (config.get("DefaultBoardName") or "Board").strip()
