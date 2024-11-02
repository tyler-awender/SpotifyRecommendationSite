# represents a Spotify playlist
class Playlist:
    
    # a Ploylidt contains a name and Spotify Playlist id
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __str__(self):
        return f"Playlist{self.name}"