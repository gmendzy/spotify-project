from flask import Flask, render_template, request, redirect, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from datetime import datetime
from dotenv import load_dotenv
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")


client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = Spotify(client_credentials_manager=client_credentials_manager)


#For creating playlists
scope = 'playlist-modify-public'


cache_handler = FlaskSessionCacheHandler(session)

#For connecting to Spotify
sp_oauth = SpotifyOAuth(
    client_id = client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

spLogin = Spotify(auth_manager=sp_oauth)









filtered_tracks = []
saved_song = {}
saved_genre ={}



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login')
def connect_spotify():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect('/create_playlist')

@app.route('/search')
def search():
    q = request.args.get('song_name')

    if q:
        results = sp.search(q=q, limit=9)
    else:
        results = []

    return render_template('search_results.html', results=results['tracks']['items'])

@app.route('/submit')
def submit():
    return render_template('submit.html')

@app.route('/choose_song', methods=['POST', 'GET'])
def choose_song():
    global saved_song 
    
    song_id = request.form.get('song_id')
    saved_song = sp.track(song_id)
    return redirect('/questionnaire')  

@app.route('/create_playlist')
def create_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    user = spLogin.current_user()
    user_ID = user['id']


    
    playlist = spLogin.user_playlist_create(user=f"{user_ID}", name="MusicGenie Playlist",
                                             public=True, description="Created by MusicGenie"
                                             )
    
    playlist_ID = playlist['id']


    track_uris = [song['uri'] for song in filtered_tracks]
    print(track_uris)

    spLogin.user_playlist_add_tracks(user=f"{user_ID}",playlist_id = playlist_ID,
                                          tracks=track_uris)
    
    return redirect("/")


@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')


@app.route('/generate_playlist_from_questionnaire', methods=['POST'])
def generate_recommendations():

    if 'saved_song' not in globals():
        return "No song selected. Please go back and select a song."
    
    
    mood = request.form.get('mood')
    activity = request.form.get('activity')
    duration = request.form.get('duration')
    popularity = request.form.get('popularity') # Popularity is determined by the total number of plays a track has had and how recent those plays are
    time_period = request.form.get('time_period')
    
    # Gets the audio features of the saved song and copies them to the target features so that we can modify them
    saved_song_attributes = sp.audio_features(saved_song['id'])[0]
    target_features = saved_song_attributes.copy()    


    artist_id = saved_song['artists'][0]['id']
    artist = sp.artist(artist_id)

    genres = artist['genres']
    seed_genre = genres[0] if genres else None

    if 'happy' in mood:
        target_features['valence'] += 0.4 # Increase relative valence
    elif 'sad' in mood:
        target_features['valence'] -= 0.2 # Decrease relative valence
    elif 'Neither' in mood:
        target_features = target_features # No change in valence
    
    if 'studying' in activity:
        target_features['energy'] -= 0.2 # Decrease relative energy
    elif 'party' in activity:
        target_features['energy'] += 0.2 # Increase relative energy
    elif 'chilling' in activity:
        target_features['tempo' ] -= 20 # Decrease relative tempo
    
    
    
    # Ensure that the target features are within the valid range
    target_features['valence'] = min(max(target_features['valence'], 0), 1)
    target_features['energy'] = min(max(target_features['energy'], 0), 1)
    target_features['tempo'] = min(max(target_features['tempo'], 0), 200)


    recommendations = sp.recommendations(
        seed_tracks =  [saved_song['id']],
        seed_genres = [seed_genre],
        target_valence = target_features['valence'],
        target_energy = target_features['energy'],
        target_tempo = target_features['tempo'],
        limit = 100
    )

    # Filter tracks based on duration and popularity since the Spotify API does not support these parameters
    conditions = {
        'short': lambda track: track['duration_ms'] <= 120000,
        'long': lambda track: track['duration_ms'] > 240000,
        'popular': lambda track: track['popularity'] > 70,
        'unpopular': lambda track: track['popularity'] < 30,
        'no preference': lambda track: True,
    }

    time_periods = {
        '90s' : ('1990-01-01', '1999-12-31'),
        '2000s' : ('2000-01-01', '2009-12-31'),
        '2010s' : ('2010-01-01', '2019-12-31'),
        '2020s' : ('2020-01-01', '2021-12-31')
    }
    start_date, end_date = time_periods[time_period]
    
    
    
    for track in recommendations['tracks']:
        album = sp.album(track['album']['id'])
        release_date = album['release_date']

        if (conditions[duration](track) and conditions[popularity](track) and 
            start_date <= release_date <= end_date):
            filtered_tracks.append(track)
            
        
    if filtered_tracks:
        return render_template('results.html', playlist_data=filtered_tracks)
    else:
        return "No tracks found with the selected criteria. Please try again."


if __name__ == '__main__':
    app.run(debug=True)
