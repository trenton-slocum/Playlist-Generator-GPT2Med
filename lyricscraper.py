import requests
import json
from bs4 import BeautifulSoup
import re


def grab_playlist_tracks(playlist_id, headers):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/"
    r = requests.get(url, headers=headers)
    if not r.status_code == 200:
        print(r.status_code)

    playlist_json = json.loads(r.text)
    playlist_tracks = playlist_json['tracks']['items']
    tracks = [playlist_track['track'] for playlist_track in playlist_tracks]

    return tracks


def get_genius_url(song_title, artist, genius_token, verbose=False):
    if "instrumental" in song_title.lower():
        return None
    if verbose:
        print(f"Searching for: {song_title} by {artist}")
    BASE_URL = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {genius_token}"}
    cleaned = re.sub(r"\s*[\(\[].*?[\)\]]|\s*-\s*.*", "", song_title)
    # Create search variants
    search_variants = [
        song_title,
        cleaned,
        f"{artist} {cleaned}",
        f"{cleaned} {artist}",
        f"{song_title} {artist}",
        f"{artist} {song_title}"
    ]

    for query in list(set(search_variants)):
        params = {"q": query}
        response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        if not response.status_code == 200:
            print(response.status_code)
        data = response.json()

        if data["response"]["hits"]:
            top_result = data["response"]["hits"][0]["result"]

            # Check if the matched song is by the correct artist
            genius_artist = top_result["primary_artist"]["name"].lower()
            if artist.lower() in genius_artist:
                return f"https://genius.com{top_result['path']}"  # Return first valid match

    print(f"No valid match found for: {song_title} by {artist}")
    return None


def scrape_lyrics(genius_url, verbose=False):
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(genius_url, headers=headers)

    if response.status_code != 200:
        print("Error: Unable to fetch the page")
        return None
    if verbose:
        print(f"Fetching lyrics from: {genius_url}")
    soup = BeautifulSoup(response.text, "html.parser")

    lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})

    # Extract text from all matching divs
    lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])

    return lyrics.strip()
