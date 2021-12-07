import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
import datetime
from PIL import Image, ImageFont, ImageDraw
import os
import random
import base64

client_id = "099bfd618f6a4e668aab271bc6761720"
client_secret = "93616a9f12ef40c998205ce4d6282622"
redirect_uri = "http://127.0.0.1:9090"

month = datetime.datetime.now().strftime("%B")


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
    generate_cover(month, id)


def dominant_color_generator(month):
    colors = ["white", "white", "green", "green", "green", "yellow",
              "yellow", "yellow", "orange", "orange", "orange", "white"]
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]
    generated_color = colors[months.index(month)]
    return generated_color


def upload_cover(playlist_id):
    scope = "ugc-image-upload"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    # reformat encoding jpg -> base64
    image = open("dataset/thumbnail.jpg", 'rb')
    image_read = image.read()
    cover_encoded = base64.b64encode(image_read).decode("utf-8")
    spotify.playlist_upload_cover_image(playlist_id, cover_encoded)


def generate_cover(query, playlist_ID):
    from google_images_search import GoogleImagesSearch
    gis = GoogleImagesSearch(
        'AIzaSyChvQNUot0_kNFim2RCCi8sN3Ytr6wrHB4', '13e74226706cfb771')
    _search_params = {
        'q': query + " wallpaper 4k nature unsplash",
        'num': 1,
        'fileType': 'jpg',
        'imgType': 'photo',
        'imgDominantColor': dominant_color_generator(query),
        'imgColorType': 'color'
    }
    gis.search(search_params=_search_params, path_to_dir='dataset',
               width=600, height=600, custom_image_name='asset')
    print("[INFO] Downloaded dataset")
    print("[INFO] Generating Thumbnail...")
    font_type = "dataset/fonts/" + random.choice(os.listdir("dataset/fonts/"))
    font = ImageFont.truetype(font_type, 130, encoding="unic")
    img = Image.open("dataset/asset.jpg")

    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(month, font=font)
    W, H = (600, 600)

    draw.text(((W-w)/2, (H-h)/2), month, (255, 255, 255), font=font)
    img.save("dataset/thumbnail.jpg")
    os.remove("dataset/asset.jpg")
    print("[INFO] cover rendered")
    upload_cover(playlist_ID)


backup_month()
#generate_cover("November", "3rLSr3hI8mH6cFWFw8MNtN")
