from django.shortcuts import render
import pandas as pd
import models.Model as model
from django.shortcuts import redirect

song_data = pd.read_csv('song_data.csv')
song_data.set_index('Song_ID', inplace=True)

def index(request):
    prompt = ''
    previous_prompts = request.session.get('previous_prompts', {})
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')

        if prompt and prompt not in previous_prompts:

            output = model.generate_playlist(prompt, max_length=500)
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
    print(output)
    songs = output.split('\n')
    songs_clean = [song.split(' -')[0] for song in songs]
    songs_clean = [song.split(' : ')[0] for song in songs_clean]
    songs_clean = list(set(songs_clean))
    tracks = []
    for song in songs_clean:
        matches = song_data[song_data['Song_Name'] == song]
        if matches.empty:
            matches = song_data[song_data['Song_Name'].str.contains(song, case=False, na=False, regex=False)]
        try:
            matches = matches[~matches['Song_Name'].str.contains('lofi', case=False, na=False, regex=False)]
            match = matches.iloc[0]
            tracks.append({
                'title': match['Song_Name'],
                'artist': match['Artist_Name'],
                'url': match['Spotify_URL']
            })
        except IndexError:
            pass
    return tracks
