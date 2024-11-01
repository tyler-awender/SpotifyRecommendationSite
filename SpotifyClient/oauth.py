from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get # to allow for post requests

# load environment variables
load_dotenv() 

# store client_id and client_secret from env file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

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
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)

token = get_token()
search_for_artist(token, "Common Kings")
