from flask import Flask, render_template, request, redirect, session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = Spotify(client_credentials_manager=client_credentials_manager)


app = Flask(__name__)

saved_song = {}
saved_genre ={}



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    song_name = request.form.get('song_name')
    results = sp.search(q=song_name, limit=5)
    return render_template('search_results.html', results=results['tracks']['items'])



@app.route('/choose_song', methods=['POST', 'GET'])
def choose_song():
    global saved_song
    song_id = request.form.get('song_id')
    saved_song = sp.track(song_id)
    return redirect('/questionnaire')   



@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')


@app.route('/generate_playlist_from_questionnaire', methods=['POST'])
def generate_recommendations():
    
    if 'saved_song' not in globals():
        return "No song selected. Please go back and select a song."
    
    mood = request.form.get('mood')
    
    artist_id = saved_song['artists'][0]['id']
    artist = sp.artist(artist_id)

    genres = artist['genres']
    seed_genre = genres[0] if genres else None

    target_valence = 0
    target_energy = 0

    if mood == "happy":
        target_energy = 1
        target_valence = 0.5
    elif mood == "sad":
        target_energy = 0.2
        target_valence = 0


    recommendations = sp.recommendations(seed_tracks=[saved_song['id']], seed_genres=[seed_genre], target_valence=target_valence, target_energy=target_energy, limit=5)



    if 'tracks' in recommendations:
        playlist_data = recommendations['tracks']
        return render_template('results.html', playlist_data=playlist_data)
    else:
        return "No recommendations were found with the desired mood."

if __name__ == '__main__':
    app.run(debug=True)
