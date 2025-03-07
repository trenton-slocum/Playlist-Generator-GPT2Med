import requests
import json

def get_playlist_ids(query, headers, limit=50):
    url = f"https://api.spotify.com/v1/search?q={query}&type=playlist&limit={limit}"
    r = requests.get(url, headers=headers)
    if not r.status_code == 200:
        print(r.status_code)

    results = r.json()
    playlist_ids = [playlist['id'] for playlist in results['playlists']['items'] if playlist]
    return playlist_ids

def get_playlist_title(playlist_id, headers):
    base_url = "https://api.spotify.com/v1/playlists/"
    r = requests.get(base_url+playlist_id, headers=headers)
    if not r.status_code == 200:
        print(r.status_code)

    playlist_json = r.json()
    name = playlist_json['name']
    return name

def get_playlist_tracks(playlist_id, headers):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/"
    r = requests.get(url, headers=headers)
    if not r.status_code == 200:
        print(r.status_code)

    playlist_json = json.loads(r.text)
    playlist_tracks = playlist_json['tracks']['items']
    tracks = [playlist_track['track'] for playlist_track in playlist_tracks]

    return tracks

def get_track_ids(playlist_id, headers):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/"
    r = requests.get(url, headers=headers)
    if not r.status_code == 200:
        print(r.status_code)

    playlist_json = json.loads(r.text)
    playlist_tracks = playlist_json['tracks']['items']
    tracks = [playlist_track['track']['id'] for playlist_track in playlist_tracks]