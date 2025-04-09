import unicodedata

import requests
from bs4 import BeautifulSoup
import re
import time
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
    "Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]


def normalize_text(text):
    """Normalize text for consistent comparison."""
    if text is None:
        return ""

    text = unicodedata.normalize("NFC", text)  # Normalize Unicode
    text = text.replace("’", "'").replace("‘", "'")  # Fix apostrophes
    text = text.replace("“", '"').replace("”", '"')  # Fix quotes
    text = text.replace("–", "-").replace("—", "-")  # Fix dashes
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))  # Remove accents
    return text.lower()  # Convert to lowercase for case-insensitive comparison


def grab_playlist_tracks(playlist_id, headers):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error {r.status_code}: Failed to fetch playlist tracks")
        return []

    playlist_json = r.json()
    playlist_tracks = playlist_json.get('tracks', {}).get('items', [])
    return [track['track'] for track in playlist_tracks if track.get('track')]


def get_genius_url(song_title, artist, genius_token, verbose=False, max_retries=5):
    song_title = normalize_text(song_title)
    artist = normalize_text(artist)

    skips = [
        'instrumental',
        'cover',
        'lullaby version',
        'lofi',
        'lo fi',
        'hz'
    ]
    if any(x in song_title.lower() for x in skips):
        print(f"No valid match found for: {song_title} by {artist}")
        return None
    if verbose:
        print(f"Searching for: {song_title} by {artist}")
    base_url = "https://api.genius.com"
    session = requests.Session()

    # Clean the song title for better matching
    cleaned = re.sub(r"\s*[(\[].*?[)\]]|\s*-\s*.*", "", song_title)

    # Create search variants
    search_variants = [
        cleaned,
        f"{artist} {cleaned}",
        f"{cleaned} {artist}",
        song_title,
        f"{song_title} {artist}",
        f"{artist} {song_title}"
    ]
    if verbose:
        print("Search Variants: ", search_variants)
    retries = 0
    while retries < max_retries:
        time.sleep(1)
        if retries > 0:
            print(f"Retry {retries}")
        headers = {
            "Authorization": f"Bearer {genius_token}",
            "User-Agent": random.choice(USER_AGENTS)  # Rotate user-agents
        }
        for query in search_variants:  # Try different search variants
            params = {"q": query}
            response = session.get(f"{base_url}/search", headers=headers, params=params)

            # Rate limit handling
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", random.uniform(10, 30)))
                print(f"Rate limit hit while fetching URLs! Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
                break  # Exit the loop and retry after sleeping

            # Retry only if response is not 200
            if response.status_code != 200:
                wait_time = 2 ** retries + random.uniform(1, 3)
                print(f"Request failed ({response.status_code}). Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                retries += 1
                break  # Exit loop and retry

            # If we get a successful response, process results
            data = response.json()
            if data["response"]["hits"]:
                for result in data["response"]["hits"]:
                    genius_artist = normalize_text(result["result"]["primary_artist"]["name"])
                    genius_title = normalize_text(result["result"]["title"])
                    lyric_state = result["result"]["lyrics_state"]
                    if (artist.lower() in genius_artist) and (cleaned.lower() in genius_title):
                        if lyric_state == 'unreleased':
                            print(f"No valid match found for: {song_title} by {artist}")
                            return None
                        return f"https://genius.com{result['result']['path']}"
                    elif (artist.lower() in [normalize_text(x['name']) for x in result["result"]["primary_artists"]]
                          and (cleaned.lower() in genius_title)):
                        if lyric_state == 'unreleased':
                            print(f"No valid match found for: {song_title} by {artist}")
                            return None
                        return f"https://genius.com{result['result']['path']}"
                    elif (artist.lower() in [normalize_text(x['name']) for x in result["result"]["featured_artists"]]
                          and (cleaned.lower() in genius_title)):
                        if lyric_state == 'unreleased':
                            print(f"No valid match found for: {song_title} by {artist}")
                            return None
                        return f"https://genius.com{result['result']['path']}"

        print(f"No valid match found for: {song_title} by {artist}")
        return None
    print(f"No valid match found for: {song_title} by {artist}")
    return None


def scrape_lyrics(genius_url, verbose=False, max_retries=5):
    if not genius_url:
        return "Lyrics not found"

    session = requests.Session()  # Use a session for connection reuse
    retries = 0

    while retries < max_retries:
        headers = {"User-Agent": random.choice(USER_AGENTS)}  # Rotate user-agents
        response = session.get(genius_url, headers=headers)

        # If we hit a rate limit (HTTP 429), wait and retry
        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", random.uniform(10, 30)))  # Use header value or fallback
            print(f"Rate limit hit! Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
            continue

        # If the request failed, retry with exponential backoff
        if response.status_code != 200:
            wait_time = 2 ** retries + random.uniform(1, 3)  # Exponential backoff
            print(f"Request failed ({response.status_code}). Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            retries += 1
            continue

        if verbose:
            print(f"Fetching lyrics from: {genius_url}")

        soup = BeautifulSoup(response.text, "html.parser")

        lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})

        # Extract text from all matching divs
        lyrics = "\n".join([div.get_text(separator="\n").strip() for div in lyrics_divs])
        lyrics = re.sub(r'^.*?Lyrics\n', '', lyrics, flags=re.S).strip()
        lyrics = re.sub(r'^.*?Read More\n\xa0\n', '', lyrics, flags=re.S).strip()
        before, sep, after = lyrics.partition("[")
        lyrics = sep + after if sep else before
        if lyrics.strip():
            return lyrics.strip()
        print('no lyrics found for: ', genius_url)
        return "Lyrics not found"

    print("Max retries reached. Skipping this song.")
    return "Lyrics not found"
