import os

from flask import Flask, render_template, send_from_directory, session

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

# we should put these in environment variables or something later
client_id = 'f4968da54d444c79b4f9296ba647de85'
client_secret = '755f3f594b074d1fb6a7cf8758fd0646'
redirect_uri = 'http://localhost:5000/callback'
scope = "playlist-read-private"

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(auth_manager=sp_oauth)



# default page
@app.route("/") 
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)