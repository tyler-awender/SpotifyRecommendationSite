# from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get # to allow for post requests

from Track import Track
from Playlist import Playlist
# load environment variables
# load_dotenv() 

# store client_id and client_secret from env file
# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")

client_id = "f4968da54d444c79b4f9296ba647de85"
client_secret = "755f3f594b074d1fb6a7cf8758fd0646"

# sends authorization request for access token
def get_token():
    # format authorization string of client id and secret to be base64 encoded
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    # make post request
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)

    # retrieve access token
    token = json_result["access_token"]
    return token

# constructs header for future requests
def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

# test function to see if token and API request works

'''
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)
'''
# ISSUE FOUND: NEED TO SETUP USER
# LOGIN TO GET THE USER'S TOKEN
# CLIENT CREDENTIALS DO NOT HAVE 
# REQUIRED PRIVILEGES/CANT FIND USER
# TRACKS THAT HAVE RECENTLY BEEN PLAYED
def get_last_played_tracks(token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = get_auth_header(token)


    result = get(url, headers=headers)

        # Check for a successful response
    if result.status_code != 200:
        print(f"Error: {result.status_code}, {result.json()}")
        return []

    response_json = result.json()

    # Handle missing 'items' key
    if "items" not in response_json:
        print("No recently played tracks found.")
        return []
    
    response_json = result.json()
    tracks = [Track(track["track"]["name"], 
                    track["track"]["id"], 
                    track["track"]["artists"][0]["name"]) 
                    for track in response_json["items"]
            ]
    return tracks


token = get_token()
get_last_played_tracks(token)
# for testing token 
# search_for_artist(token, "Common Kings")
