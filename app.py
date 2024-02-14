from flask import Flask, render_template, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = Spotify(client_credentials_manager=client_credentials_manager)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/generate_playlist', methods=['POST'])
def generate_recommendations():
    
    song_name = request.form.get('song_name')

    try:

        search_results = sp.search(q=song_name, type='track', limit=1)
        track_id = search_results['tracks']['items'][0]['id']

        recommendations = sp.recommendations(seed_tracks=[track_id], limit=5)

        if 'tracks' in recommendations:
            playlist_data = recommendations['tracks']
            return render_template('results.html', playlist_data=playlist_data)
        else:
            return render_template('error.html', error_message ='No recommendations found.')
    except Exception as e:
        return render_template('error.html', error_message=str(e))
    
if __name__ == '__main__':
    app.run(debug=True)

