from django.shortcuts import render
import pandas as pd


song_data = pd.read_csv('song_data.csv')
song_data.set_index('Song_ID', inplace=True)

def index(request):
    track_ids = ['2meEiZKWkiN28gITzFwQo5',
              '1OXfWI3FQMdsKKC6lkvzSx',
              '5jrdCoLpJSvHHorevXBATy',
              '4pSPMXaCjbaV3VSzZQYC7H',
              '7BKLCZ1jbUBVqRi2FVlTVw',
                 'fake_id',
              '3rUGC1vUpkDG9CZFHMur1t',
              '1mea3bSkSGXuIRvnydlB5b',
              '6Knv6wdA0luoMUuuoYi2i1',
              '4iJyoBOLtHqaGxP12qzhQI',
              '4LRPiXqCikLlN15c3yImP7'
              ]
    tracks = []
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        for song_id in track_ids:
            if song_id in song_data.index:
                song = song_data.loc[song_id]
                tracks.append({
                    'title': song['Song_Name'],
                    'artist': song['Artist_Name'],
                    'url': song['Spotify_URL']
                })

    return render(request, 'generator/index.html', {'tracks': tracks})
