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
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    results = search_spotify(query)
    return render_template('index.html', results=results)

def search_spotify(query):
    results = sp.search(q=query, type='track', limit=5)

    return results['tracks']['items']['id']

if __name__ == '__main__':
    app.run(debug=True)

