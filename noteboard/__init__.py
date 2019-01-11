import os
# Paths
DIR_PATH = os.path.join(os.path.expanduser("~"), ".noteboard/")
LOG_PATH = os.path.join(DIR_PATH, "noteboard.log")
STATES_PATH = os.path.join(DIR_PATH, "states.pkl.gz")
STORAGE_PATH = os.path.join(DIR_PATH, "storage")
STORAGE_GZ_PATH = os.path.join(DIR_PATH, "storage.gz")
if not os.path.isdir(DIR_PATH):
    os.mkdir(DIR_PATH)

from .storage import Storage
