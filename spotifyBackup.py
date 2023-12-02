import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
import datetime
from openai import OpenAI
import base64
import requests
import json

# read file "secrets.txt" and extract keys
with open("secrets.txt", "r") as f:
    SPOTIFY_CLIENT_ID = f.readline().strip()
    SPOTIFY_CLIENT_SECRET = f.readline().strip()
    OPENAI_API_KEY = f.readline().strip()
    f.close()

redirect_uri = "http://127.0.0.1:9090"


def get_liked_songs():
    scope = "user-library-read"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))
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
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))
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
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))
    playlists = []
    results = spotify.current_user_playlists()
    for playlist in results["items"]:
        playlists.append(playlist["name"])
    return playlists


def create_playlist():
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))
    # get current month and year but ony last 2 digits
    month  = datetime.datetime.now().strftime("%B %y")
    description = "Your favorites from " + month
    if month not in get_playlists():
        id = spotify.user_playlist_create(
            user="vfroehlich", name=month, public=False, collaborative=False, description=description)
        return id["id"]
    else:
        return


def playlist_add_songs(songs, id=create_playlist()):
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))
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
    upload_cover(id)


def upload_cover(playlist_id):
    scope = "ugc-image-upload"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))
    # reformat encoding jpg -> base64
    img_url = image_generator(month)
    cover_encoded = text_overlay(img_url)
    print(type(cover_encoded))
    spotify.playlist_upload_cover_image(playlist_id, cover_encoded)


def image_generator(month):
    # we're going to call openai API here to generate an image
    #initialize API key
    client = OpenAI(api_key=OPENAI_API_KEY)
    # call API
    response = client.images.generate(
        model="dall-e-2",
        prompt=promt_gen(month),
        size="512x512",
        quality="standard",
        n=1,
        )

    image_url = response.data[0].url
    return image_url

def promt_gen(month):
    if month in ["December", "January", "February"]:
        return "beautiful winter night landscape with mountains and trees in snow, wide angle"
    elif month in ["March", "April", "May"]:
        return "Gorgeous early spring young leaves in a fresh forest landscape, elegant, high definition, sharp focus, wide angle, wallpaper"
    elif month in ["June", "July", "August"]:
        return "beautiful summer landscape with mountains and trees in snow, wide angle"
    else:
        return "spectacular autumn forest landscape, fall coloring, mountains in the background, ray tracing, vivid alive vibrant colors, pure nature, perfect, finding solace"


def text_overlay(img_url):
    # add text to image using PIL
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(requests.get(img_url, stream=True).raw)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("dataset/fonts/PS.ttf", 16)
    # draw the text in the middle of the image and center it
    W, H = img.size
    _, _, w, h = draw.textbbox((0, 0), month, font=font)
    draw.text(((W-w)/2,(H-h)/2), month, fill="white", font=font)
    # convert image to base64
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


if __name__ == "__main__":
    month = datetime.datetime.now().strftime("%B")
    print("Backing up your favorite songs from " + month)
    image_generator(month)
    
    # get liked songs
    likedSongs = get_liked_songs()
    print("[INFO] " + str(len(likedSongs)) + " liked songs found")
    # get top songs from that month
    topSongs = get_top_songs()
    print("[INFO] " + str(len(topSongs)) + " top songs found")
    # add top songs to playlist
    backup_month()