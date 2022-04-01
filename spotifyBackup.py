import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
import datetime
from PIL import Image, ImageFont, ImageDraw
import os
import random
import base64

from image_generator import *

client_id = "099bfd618f6a4e668aab271bc6761720"
client_secret = "93616a9f12ef40c998205ce4d6282622"
redirect_uri = "http://127.0.0.1:9090"


def get_liked_songs():
    scope = "user-library-read"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
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
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    topSongs = []
    for i in range(100):
        results = spotify.current_user_top_tracks(
            limit=50, offset=50*i, time_range='short_term')
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
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    playlists = []
    results = spotify.current_user_playlists()
    for playlist in results["items"]:
        playlists.append(playlist["name"])
    return playlists


def create_playlist():
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    name = month
    description = "Your favorites from " + month
    if month not in get_playlists():
        id = spotify.user_playlist_create(
            user="vfroehlich", name=name, public=False, collaborative=False, description=description)
        return id["id"]
    else:
        return


def playlist_add_songs(songs, id=create_playlist()):
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    if id is not None:
        spotify.user_playlist_add_tracks(
            user="vfroehlich", playlist_id=id, tracks=songs, position=None)
        return id
    else:
        return False


def playlist_chunks(list=extract_id(), n=100):
    for i in range(0, len(list), n):
        yield list[i:i + n]


def backup_month():
    for go in list((playlist_chunks())):
        id = playlist_add_songs(songs=go)
        if id != False:
            print("[INFO] Playlist successfully created")
        else:
            print("[WARNING] Playlist already exists")
            break
    render_pass = generate_cover(month)
    if render_pass == True:
        upload_cover(playlist_id=id)


def upload_cover(playlist_id):
    scope = "ugc-image-upload"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    # reformat encoding jpg -> base64
    with open("dataset/thumbnail.jpg", 'rb') as image:
        cover_encoded = resize_as_base64(image)#base64.b64encode(image.read()).decode("utf-8")
        spotify.playlist_upload_cover_image(playlist_id, cover_encoded)



backup_month()