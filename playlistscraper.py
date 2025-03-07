import requests
import json
import time

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
    tracks = [playlist_track['track']['name'] for playlist_track in playlist_tracks]
    ids = [playlist_track['track']['id'] for playlist_track in playlist_tracks]

    return name, tracks, ids