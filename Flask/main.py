import os
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = 'f4968da54d444c79b4f9296ba647de85'
client_secret = '755f3f594b074d1fb6a7cf8758fd0646'
redirect_uri = 'http://localhost:5000/callback'
# Updated scope to include necessary permissions
scope = "playlist-read-private user-top-read user-library-read"

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

def get_track_features(track_id):
    """Get audio features for a track"""
    return sp.audio_features([track_id])[0]

def get_recommendations(seed_tracks, limit=10):
    """Get recommendations based on seed tracks"""
    try:
        recommendations = sp.recommendations(
            seed_tracks=seed_tracks[:5],  # Spotify allows max 5 seed tracks
            limit=limit,
            min_popularity=20,
            target_popularity=60
        )
        
        # Enhance recommendations with additional track info
        enhanced_recommendations = []
        for track in recommendations['tracks']:
            features = get_track_features(track['id'])
            enhanced_recommendations.append({
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'spotify_url': track['external_urls']['spotify'],
                'preview_url': track['preview_url'],
                'popularity': track['popularity'],
                'energy': features['energy'] if features else None,
                'danceability': features['danceability'] if features else None,
                'tempo': features['tempo'] if features else None
            })
        
        return enhanced_recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

@app.route("/")
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('recommendation_page'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('recommendation_page'))

@app.route('/recommendation_page')
def recommendation_page():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    # Get user's top tracks
    top_tracks = sp.current_user_top_tracks(limit=20, time_range='medium_term')
    
    # Get user's playlists for the dropdown
    playlists = sp.current_user_playlists()
    
    return render_template(
        'recommendations.html',
        top_tracks=top_tracks['items'],
        playlists=playlists['items']
    )

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_route():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return jsonify({'error': 'Not authenticated'}), 401
    
    source = request.form.get('source', 'top_tracks')
    playlist_id = request.form.get('playlist_id')
    
    try:
        if source == 'top_tracks':
            top_tracks = sp.current_user_top_tracks(limit=20)
            seed_tracks = [track['id'] for track in random.sample(top_tracks['items'], min(5, len(top_tracks['items'])))]
        else:
            playlist_tracks = sp.playlist_tracks(playlist_id)
            seed_tracks = [track['track']['id'] for track in random.sample(playlist_tracks['items'], min(5, len(playlist_tracks['items'])))]
        
        recommendations = get_recommendations(seed_tracks)
        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)