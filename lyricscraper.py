import requests
import json
from bs4 import BeautifulSoup


def grab_playlist_tracks(playlist_id, headers):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/"
    r = requests.get(url, headers=headers)
    if not r.status_code == 200:
        print(r.status_code)

    playlist_json = json.loads(r.text)
    playlist_tracks = playlist_json['tracks']['items']
    tracks = [playlist_track['track'] for playlist_track in playlist_tracks]

    return tracks

def get_genius_url(song_title, artist, genius_token):
    BASE_URL = "https://api.genius.com"
    search_url = f"{BASE_URL}/search"
    headers = {"Authorization": f"Bearer {genius_token}"}
    params = {"q": f"{song_title} {artist}"}

    response = requests.get(search_url, headers=headers, params=params)

    data = response.json()

    if data["response"]["hits"]:
        song_path = data["response"]["hits"][0]["result"]["path"]
        song_url = f"https://genius.com{song_path}"
    else:
        print("No songs found")
        song_url = None
    return song_url

def scrape_lyrics(genius_url):
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(genius_url, headers=headers)

    if response.status_code != 200:
        print("Error: Unable to fetch the page")
        return None

    print(f"Fetching lyrics from: {genius_url}")
    soup = BeautifulSoup(response.text, "html.parser")

    lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})

    # Extract text from all matching divs
    lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])

    return lyrics.strip()

