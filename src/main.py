import util
import pathlib
import time
from logger import log
from config import BASE_PATH, UPDATE_LYRICS_TAG

# Use glob to get a list of file paths matching the pattern
file_paths = BASE_PATH.glob("**/*.flac")

def retry(max_retries, delay_second=0):
    """
    Retry decorator with exponential backoff.

    :param max_retries: Maximum number of retries.
    :param delay: Initial delay between retries in seconds.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Retry {retries + 1}/{max_retries} - Exception: {e}")
                    time.sleep(delay_second)
                    retries += 1
            raise Exception(f"Max retries ({max_retries}) reached. Last exception: {e}")
        return wrapper
    return decorator

@retry(max_retries=3, delay_second=30)
def handle_file(idx: int, path: pathlib.Path):
    log.info(f"[{idx:06}] Processing {path}")
    tags = util.get_tags(path, ["ISRC", "USLT"])
    isrc_tag, lyric_tag = tags["ISRC"], tags["USLT"]
    if not isrc_tag["found"]:
        log.info(f"[{idx:06}] Skipping process, failed to get ISRC")
        return
    elif not UPDATE_LYRICS_TAG and lyric_tag["found"]:
        log.info(f"[{idx:06}] Skipping process, already has lyrics tag")
        return

    isrc = isrc_tag["value"]
    log.info(f"[{idx:06}] ISRC: {isrc}")

    try:
        searchResponse = util.search_tracks(f"isrc:{isrc}")
    except Exception as e:
        log.error(f"[{idx:06}] Failed to search track", exc_info=e)
        return
    if len(searchResponse.items) == 0:
        log.info(f"[{idx:06}] No track found, skipping entry")
        return

    for track in searchResponse.items:
        track_id = track["id"]
        log.info(f"[{idx:06}] Got processing track result {",".join(track["artists"])} - {track["name"]} [{track["id"]}]")

        log.info(f"[{idx:06}] Fetching lyrics for track id {track_id}")
        try:
            lrc_lyrics = util.get_lrc_lyrics(track_id)
        except util.NoLyricsFound as e:
            log.info(f"[{idx:06}] No lyrics found for track id {track_id}")
            continue
        except Exception as e:
            log.error(f"[{idx:06}] Failed to get lyric due to unknown error", exc_info=e)
            continue
        log.info(f"[{idx:06}] Success fetch lyrics for track id {track_id}")
        
        log.info(f"[{idx:06}] Start tagging music with lyrics tag")
        util.tag_with_lyrics(music_path=path, lyrics=lrc_lyrics)
        log.info(f"[{idx:06}] Finish tagging lyrics tag")
        break
    time.sleep(1)

for idx, path in enumerate(file_paths):
    try:
        handle_file(idx, path)
    except Exception as e:
        log.error(f"[{idx:06}] Fatal error", exc_info=e)
else:
    log.info(f"No files were found at {BASE_PATH}")

