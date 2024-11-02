# represent a song on Spotify
class Track:

    # contains a track name, Spotify track id, and artist name
    def __init__(self, name, id, artist):
        self.name = name
        self.id = id
        self.artist = artist

    def create_spotify_url(self):
        return f"spotify:track:{self.id}"
    
    def __str__(self):
        return f"{self.name} by {self.artist}"

