import math
import os
import re
from collections import namedtuple
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


load_dotenv()

GOOD_ALBUMS_PLAYLIST_ID = "PLP4CSgl7K7opy6_w-ie2fQo4U7WbgHRlJ"
YT_API_KEY = os.getenv("YT_API_KEY")
yt_service = build('youtube', 'v3', developerKey=YT_API_KEY)
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


AlbumDescription = namedtuple("AlbumDescription", "artist title")

def main():
  response = yt_service.playlistItems().list(
      part="snippet", maxResults=50,
      playlistId=GOOD_ALBUMS_PLAYLIST_ID).execute()

  items = response["items"]

  num_items = response["pageInfo"]["totalResults"]
  curr_response = response
  next_page_token = curr_response["nextPageToken"]
  while "nextPageToken" in curr_response:
      curr_response = yt_service.playlistItems().list(
          part="snippet",
          maxResults=50,
          pageToken=curr_response["nextPageToken"],
          playlistId=GOOD_ALBUMS_PLAYLIST_ID).execute()
      items.extend(curr_response["items"])
  

  item_titles = []
  for video_item in items:
    item_titles.extend(titles_from_video(video_item["snippet"]["description"]))

  descriptions = []
  for t in item_titles:
    # print(t)
    artist, album_title, *rest = t.split(" - ")
    artist = re.sub(r"\d\. ", "", artist)
    album_title = re.sub(r":.+", "", album_title)
    description = AlbumDescription(artist, album_title)
    descriptions.append(description)

  
  for description in descriptions:
    artist, title = description
    results = spotify.search(f'artist:{artist} title:{title}', type="album")
    print(results)


def dl_descriptions(items):
  Path("./descriptions").mkdir(parents=True, exist_ok=True)
  for item in items:
    file_title = f"{item['snippet']['title']}.txt"
    with open(f"descriptions/{file_title}", "w") as f:
      f.write(item["snippet"]["description"])
      print(f"wrote {file_title}")


def get_recommendations_from_video(video_item):
  pass

def titles_from_video(description):
  lines = description.split("\n")
  return [l for l in lines if " - " in l]

if __name__ == "__main__":
  main()
