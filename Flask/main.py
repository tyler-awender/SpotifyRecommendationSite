import os
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import pylast
import random
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

# Last.fm API credentials
API_KEY = "9bb9084cd2af09289f944186b13734b4"
API_SECRET = "83e5071630925615829ccef4be0a2d39"

# Initialize Last.fm network
network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET
)

def get_track_info(track, artist):
    """Get additional information about a track"""
    try:
        track_obj = network.get_track(artist, track)
        return {
            'name': track,
            'artist': artist,
            'url': track_obj.get_url(),
            'listeners': track_obj.get_listener_count(),
            'playcount': track_obj.get_playcount(),
            'tags': [tag.item.name for tag in track_obj.get_top_tags(limit=5)]
        }
    except Exception as e:
        print(f"Error getting track info: {e}")
        return None

def get_recommendations(artist_name, limit=10):
    """Get recommendations based on an artist"""
    try:
        artist = network.get_artist(artist_name)
        similar_artists = artist.get_similar(limit=limit)
        
        recommendations = []
        for similar in similar_artists:
            artist_obj = similar.item
            try:
                # Get the artist's top track
                top_track = artist_obj.get_top_tracks(limit=1)[0].item
                
                recommendations.append({
                    'artist_name': artist_obj.name,
                    'artist_url': artist_obj.get_url(),
                    'track_name': top_track.get_name(),
                    'track_url': top_track.get_url(),
                    'listeners': artist_obj.get_listener_count(),
                    'tags': [tag.item.name for tag in artist_obj.get_top_tags(limit=3)]
                })
            except Exception as e:
                print(f"Error processing artist {artist_obj.name}: {e}")
                continue
                
        return recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

@app.route("/")
def home():
    return render_template('recommendations.html')

@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form.get('artist')
    try:
        recommendations = get_recommendations(artist_name)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/explore_artist/<artist_name>')
def explore_artist(artist_name):
    try:
        artist = network.get_artist(artist_name)
        top_tracks = artist.get_top_tracks(limit=10)
        
        artist_info = {
            'name': artist.name,
            'url': artist.get_url(),
            'listeners': artist.get_listener_count(),
            'top_tracks': [{
                'name': track.item.get_name(),
                'url': track.item.get_url(),
                'listeners': track.item.get_listener_count()
            } for track in top_tracks],
            'tags': [tag.item.name for tag in artist.get_top_tags(limit=5)]
        }
        
        return render_template('artist.html', artist=artist_info)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)