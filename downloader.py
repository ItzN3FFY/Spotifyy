import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
import zipfile
import requests

def expand_spotify_link(short_url):
    try:
        response = requests.get(short_url, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Error expanding link: {e}")
        return None

def detect_spotify_type(url):
    if "playlist" in url:
        return "playlist"
    elif "track" in url:
        return "track"
    elif "album" in url:
        return "album"
    else:
        return "unknown"

def get_tracks_from_playlist(url):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    ))
    playlist_id = url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    if results and 'items' in results:
        for item in results['items']:
            track = item['track']
            name = track['name']
            artist = track['artists'][0]['name']
            tracks.append(f"{name} {artist}")
    return tracks

def get_tracks_from_album(url):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    ))
    album_id = url.split("/")[-1].split("?")[0]
    results = sp.album_tracks(album_id)
    tracks = []
    if results and 'items' in results:
        for item in results['items']:
            name = item['name']
            artist = item['artists'][0]['name']
            tracks.append(f"{name} {artist}")
    return tracks

def get_track_name(url):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    ))
    track_id = url.split("/")[-1].split("?")[0]
    track = sp.track(track_id)
    if track:
        name = track['name']
        artist = track['artists'][0]['name']
        return [f"{name} {artist}"]
    return []

def get_metadata(url, link_type):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    ))
    try:
        if link_type == "playlist":
            playlist_id = url.split("/")[-1].split("?")[0]
            data = sp.playlist(playlist_id)
        elif link_type == "album":
            album_id = url.split("/")[-1].split("?")[0]
            data = sp.album(album_id)
        else:
            return None, None

        if data and 'name' in data and 'images' in data and data['images']:
            return data['name'], data['images'][0]['url']
    except Exception as e:
        print(f"Metadata fetch error: {e}")
    return None, None

def download_tracks(track_list):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        for track in track_list:
            try:
                ydl.download([f"ytsearch:{track}"])
            except Exception as e:
                print(f"Download failed for {track}: {e}")

def zip_and_cleanup(zip_name="playlist_downloads.zip"):
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for file in os.listdir():
            if file.endswith(".mp3"):
                zipf.write(file)
    return zip_name

def clear_old_downloads():
    for file in os.listdir():
        if file.endswith(".mp3") or file.endswith(".webm") or file.endswith(".zip"):
            os.remove(file)