import requests
import json
import time
import pandas as pd

def get_playlist_ids(query, headers, limit=50):
    url = f"https://api.spotify.com/v1/search?q={query}&type=playlist&limit={limit}"
    r = requests.get(url, headers=headers)
    time.sleep(1)

    if not r.status_code == 200:
        return "Status code:"+r.status_code
    results = r.json()

    playlist_ids = [playlist['id'] for playlist in results['playlists']['items'] if playlist]
    return playlist_ids

def get_playlist_data(playlist_id, headers):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    r = requests.get(url, headers=headers)
    time.sleep(1)

    if not r.status_code == 200:
        print(r.status_code)
    playlist_json = r.json()

    name = playlist_json['name']
    playlist_tracks = playlist_json['tracks']['items']
    tracks = [track['track']['name'] for track in playlist_tracks if track['track']]
    artists = [track['track']['artists'][0]['name'] for track in playlist_tracks if track['track']]
    ids = [track['track']['id'] for track in playlist_tracks if track['track']]

    return name, tracks, artists, ids

def get_playlist_df(query, headers, limit=50):
    playlist_ids = get_playlist_ids(query, headers, limit)

    playlist_data = []
    for id in playlist_ids:
        name, tracks, artists, track_ids = get_playlist_data(id, headers)
        playlist_data.append((id, name, tracks, artists, track_ids))

    df = pd.DataFrame(playlist_data)
    df.columns = ["Playlist_ID", "Playlist_Name", "Playlist_Songs", "Playlist_Artists", "Playlist_Song_IDs"]
    return df