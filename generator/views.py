from django.shortcuts import render
import pandas as pd
import Model as model
from django.shortcuts import redirect

song_data = pd.read_csv('song_data.csv')
song_data.set_index('Song_ID', inplace=True)

output = """Crazy Little Thing Called Love - Remastered 2009
I Wanna Dance with Somebody (Who Loves Me)
Stayin Alive - From "Saturday Night Fever" Soundtrack
Super Freak
Billie Jean
Jump - 2015 Remaster
September
Billie Jean
Uptown Girl
Dancing Queen
Bohemian Rhapsody - Remastered 2011
We Built This City
Girls Just Want to Have Fun
Let's Groove
More Than a Feeling
Born in the U.S.A.
Dancing Queen
Wake Me Up Before You Go-Go
Let's Groove - Sped Up
More Than A Feeling - 12" Version
Grease - From “Grease”
Girls Just Want to Have Fun
Kung Fu Fighting
I Can't Help Myself (Sugar Pie, Honey Bunch)
Don't Stop Believin'
Crocodile"""


def index(request):
    prompt = ''
    previous_prompts = request.session.get('previous_prompts', {})
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')

        if prompt and prompt not in previous_prompts:
            output = model.generate_playlist(prompt)
            tracks = song_id_lookup(output)
            previous_prompts[prompt] = tracks
            if len(previous_prompts) > 15:
                previous_prompts = dict(list(previous_prompts.items())[-15:])
            request.session['previous_prompts'] = previous_prompts
        else:
            tracks = previous_prompts.get(prompt, [])

        return render(request,
                      'generator/index.html',
                      {'tracks': tracks, 'previous_prompts': dict(reversed(list(previous_prompts.items()))), 'prompt': prompt})
    else:
        return render(request, 'generator/index.html', {
            'previous_prompts': dict(reversed(list(previous_prompts.items())))
        })

def reset_history(request):
    request.session.flush()
    return redirect('index')

def song_id_lookup(output):
    songs = output.split('\n')
    songs_clean = [song.split(' -')[0] for song in songs]
    songs_clean = [song.split(' : ')[0] for song in songs]
    songs_clean = list(set(songs_clean))

    tracks = []
    for song in songs_clean:
        matches = song_data[song_data['Song_Name'].str.contains(song, case=False, na=False, regex=False)]
        try:
            match = matches.iloc[0]
            tracks.append({
                'title': match['Song_Name'],
                'artist': match['Artist_Name'],
                'url': match['Spotify_URL']
            })
        except IndexError:
            pass
    return tracks
