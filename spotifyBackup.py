import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

client_id="099bfd618f6a4e668aab271bc6761720"
client_secret = "fcca8c7205244eecadfcb07bcadd0dd2"
redirect_uri = "http://127.0.0.1:9090"

month = datetime.datetime.now().strftime("%B")

def get_liked_songs():
    scope = "user-library-read"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    likedSongs = []
    for i in range(100):
        results = spotify.current_user_saved_tracks(limit=50, offset=50*i)
        for track in results["items"]:
            likedSongs.append(track)
        if len(results["items"]) < 50:
            break
    return likedSongs


def get_top_songs():
    scope = "user-top-read"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    topSongs = []
    for i in range(100):
        results = spotify.current_user_top_tracks(limit=50, offset=50*i, time_range='short_term')
        for track in results["items"]:
            topSongs.append(track)
        if len(results["items"]) < 50:
            break
    return topSongs


def extract_id(songs=get_top_songs()):
    IDs = []
    for song in songs:
        IDs.append(song["id"])
    return IDs


def get_playlists():
    scope = "playlist-read-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    playlists = []
    results = spotify.current_user_playlists()
    for playlist in results["items"]:
        playlists.append(playlist["name"])
    return playlists


def create_playlist():
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    name = month
    description  = "Your favorites from " + month
    if month not in get_playlists():
        id = spotify.user_playlist_create(user= "vfroehlich", name=name, public=False, collaborative=False, description=description)
        return id["id"]
    else:
        return

def playlist_add_songs(songs, id=create_playlist()):
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    if id is not None:
        spotify.user_playlist_add_tracks(user="vfroehlich", playlist_id=id, tracks=songs, position=None)
        return True
    else:
        return False


def playlist_chunks(list=extract_id(), n=100):
    for i in range(0, len(list), n):
        yield list[i:i + n]


def backup_month():
    for go in list((playlist_chunks())):
        if playlist_add_songs(songs=go) == True:
            print("[INFO] Playlist successfully created")
        else:
            print("[WARNING] Playlist already exists")


backup_month()
