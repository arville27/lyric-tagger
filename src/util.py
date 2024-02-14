from typing import List
import requests
import taglib
import pathlib
import math
from logger import log
from config import SPLYR_API_HOST

class Track:
    id: str
    name: str
    aritsts: List[str]

class SearchResponse:
    items: List[Track]
    page: int
    totalItems: int
    maxPage: int

class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

class NoLyricsFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def search_tracks(query: str) -> SearchResponse:
    response = requests.get(
        url=f"{SPLYR_API_HOST}/splyr",
        params={"q": query}
    )
    if not response.ok:
        log.error(f"Error {response.status_code}:\n{response.text}")
        raise RuntimeError(f"Receive not ok status code {response.status_code}, Body:\n{response.text}")
    parsedResponse = response.json()
    log.debug(f"Got {len(parsedResponse["items"])} result(s)")
    return Map(parsedResponse)

def format_millis(timestamp_ms: int): 
  minutes = math.floor(timestamp_ms / 1000 / 60);
  seconds = math.floor((timestamp_ms / 1000) % 60);
  millis = math.floor((timestamp_ms % 1000) / 10);
  return f"{minutes:02}:{seconds:02}.{millis:02}"

def get_lrc_lyrics(track_id: str) -> str:
    if len(track_id) == 0 or len(track_id) > 22:
        raise RuntimeError("Invalid track id")
    response = requests.get(
        url=f"{SPLYR_API_HOST}/splyr/{track_id}"
    )
    if not response.ok:
        log.error(f"Error {response.status_code}:\n{response.text}")
        if response.status_code == 404:
            raise NoLyricsFound(f"No lyrics found for track id {track_id}")
        else:
            raise RuntimeError(f"Receive not ok status code {response.status_code}, Body:\n{response.text}")
    parsedResponse = response.json()
    lines = [f"[{format_millis(x["startTimeMs"])}]{x["words"]}" for x in parsedResponse["lyrics"]["lines"]]
    return "\n".join(lines)

def get_tags(music_path: pathlib.Path, tag_name: List[str]) -> dict:
    with taglib.File(music_path) as song:
        result = {}
        for tag in tag_name:
            if not tag in song.tags or len(song.tags[tag]) == 0:
                result[tag] = {"found": False, "value": None}
            else:
                result[tag] = {"found": True, "value": song.tags[tag][0]}
        return result

def get_isrc_tag(music_path: pathlib.Path) -> str:
    with taglib.File(music_path) as song:
        if not "ISRC" in song.tags or len(song.tags["ISRC"]) == 0:
            raise RuntimeError("ISRC tag unavailable")
        return song.tags["ISRC"][0]

def tag_with_lyrics(music_path: pathlib.Path, lyrics: str) -> None:
    with taglib.File(music_path, save_on_exit=True) as song:
        song.tags["LYRICS"] = [lyrics]
        song.tags["USLT"] = [lyrics]