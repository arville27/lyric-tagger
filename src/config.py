import os
from logger import log
import pathlib

all_var_present = True
if not os.getenv("SPLYR_API_HOST"):
    log.error("Please define 'SPLYR_API_HOST' environment variable")
    all_var_present = False

if not all_var_present:
    exit(1)

UPDATE_LYRICS_TAG = os.getenv("UPDATE_LYRICS_TAG") in ["True", "true", "TRUE", "1", "y", "yes", "YES"]
if UPDATE_LYRICS_TAG:
    log.info("Update lyrics tag is present, will update current lyrics tag")

BASE_PATH = pathlib.Path("/app/music")
if os.getenv("MUSIC_PATH"):
    BASE_PATH = pathlib.Path(os.getenv("MUSIC_PATH"))
else:
    log.info("No 'MUSIC_PATH' environment variable defined, use /app/music as default music directory")
    
SPLYR_API_HOST = os.getenv("SPLYR_API_HOST")
