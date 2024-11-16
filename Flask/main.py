import os
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import random

# initialize a Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)   # set a secret key for session management

# spotify API credentials
client_id = 'f4968da54d444c79b4f9296ba647de85'
client_secret = '755f3f594b074d1fb6a7cf8758fd0646'
redirect_uri = 'http://localhost:5000/callback' # redirect URI for Spotify OAuth

# Updated scope to include necessary permissions
scope = "playlist-read-private user-top-read user-library-read playlist-modify-public playlist-modify-private"

# initialize Spotify OAuth and cache handler
cache_handler = FlaskSessionCacheHandler(session) # use Flask session for cache handling
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True    # show dialog for user to re-authenticate if necessary 
)

# initialize Spotify API client
sp = Spotify(auth_manager=sp_oauth)

def get_track_features(track_id):
    """Get audio features for a track"""
    return sp.audio_features([track_id])[0] # fetch audio features for the given track ID

def get_recommendations(seed_tracks, limit=10):
    """Get recommendations based on seed tracks"""
    try:
        recommendations = sp.recommendations(
            seed_tracks=seed_tracks[:5],  # Spotify allows max 5 seed tracks
            limit=limit,                  # Limit number of recommendations to specified value (10)
            min_popularity=20,            # Set minimum popularity for recommended tracks
            target_popularity=60          # Set target popularity for recommended tracks
        )
        
        # Enhance recommendations with additional track info
        enhanced_recommendations = []
        for track in recommendations['tracks']:
            features = get_track_features(track['id'])  # get audio features for each recommended track
            enhanced_recommendations.append({
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'spotify_url': track['external_urls']['spotify'],
                'preview_url': track['preview_url'],
                'popularity': track['popularity'],
                'uri': track['uri'],  # Include the track URI
                'energy': features['energy'] if features else None,
                'danceability': features['danceability'] if features else None,
                'tempo': features['tempo'] if features else None,
                'album_cover': track['album']['images'][0]['url']  # Add album cover to recommendations
            })
        
        return enhanced_recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")    # print any errors that occur
        return []                                       # return empty list if errors occur

@app.route("/")
def home():
    # redirect to Spotify authorization page if not authenticated
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url() # generate authorization URL
        return redirect(auth_url)               # redirect user to the authorization URL
    return redirect(url_for('recommendation_page')) # redirect to the recommendation page

@app.route('/callback')
def callback():
    # handle the callback from Spotify authorization
    sp_oauth.get_access_token(request.args['code']) # get access token from authorization code
    return redirect(url_for('recommendation_page')) # redirect to recommendation page

@app.route('/recommendation_page')
def recommendation_page():
    # redirect to Spotify authorization page if not authenticated
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):   
        auth_url = sp_oauth.get_authorize_url() # generate authorization URL
        return redirect(auth_url)               # redirect user to authorization URL
    
    # Get user's top tracks
    top_tracks = sp.current_user_top_tracks(limit=20, time_range='medium_term')
    
    # Get user's playlists for the dropdown
    playlists = sp.current_user_playlists()
    
    # render the recommendations page with top tracks and playlists
    return render_template(
        'recommendations.html',
        top_tracks=top_tracks['items'],
        playlists=playlists['items']
    )

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    # redirect to Spotify authorization page
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return jsonify({'error': 'Not authenticated'}), 401 # return an error if not authenticated
    
    # get source of seed tracks (top tracks or playlist)
    source = request.form.get('source', 'top_tracks')   # default to 'top_tracks' if no source
    playlist_id = request.form.get('playlist_id')       # get playlist ID from the form data
    
    try:
        if source == 'top_tracks':
            # get user's top tracks as seed tracks
            top_tracks = sp.current_user_top_tracks(limit=20)
            seed_tracks = [track['id'] for track in random.sample(top_tracks['items'], min(5, len(top_tracks['items'])))]
        else:
            # get tracks from the selected playlist as seed tracks
            playlist_tracks = sp.playlist_tracks(playlist_id)
            seed_tracks = [track['track']['id'] for track in random.sample(playlist_tracks['items'], min(5, len(playlist_tracks['items'])))]
        
        # get recommendations based on seed tracks
        recommendations = get_recommendations(seed_tracks)

        # Extract track IDs for easier use
        track_uris = [track['uri'] for track in recommendations]

        return jsonify({'recommendations': recommendations, 'track_uris': track_uris})    # return recommendations as JSON
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # return error if an exception occurs

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # redirect to Spotify authorization page
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return jsonify({'error': 'Not authenticated'}), 401 # return an error if not authenticated

    # get name of newly created playlist from form data
    playlist_name = request.form.get('playlist_name', 'Recommended Playlist')

    # get recommended track uris from the form data
    track_uris = request.form.getlist('track_uris[]')

    # create new playlist for user
    try:
        # get id of user
        user_id = sp.current_user()['id']
        # create a new playlist usinpg user's id
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True)

        if track_uris:
            # add recommended tracks to new playlist
            sp.playlist_add_items(playlist['id'], track_uris, position=None)

        return render_template(
            'playlist.html',
            playlist = playlist,
            tracks = sp.playlist_tracks(playlist['id'])['items']
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # return error if an exception occurs


@app.route('/logout')
def logout():
    # clear session and redirect to home page
    session.clear() # clear session data    
    return redirect(url_for('home'))    # redirect to home page

if __name__ == "__main__":
    app.run(debug=True) # run Flask app in debug mode