# helper functions to graph danceability, energy, and valence of songs over playlist

# we'll use plotly to graph the data
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import plotly.graph_objects as go
import numpy as np


# read file "secrets.txt" and extract keys
with open("secrets.txt", "r") as f:
    SPOTIFY_CLIENT_ID = f.readline().strip()
    SPOTIFY_CLIENT_SECRET = f.readline().strip()
    OPENAI_API_KEY = f.readline().strip()
    f.close()

redirect_uri = "http://127.0.0.1:9090"


color_map = {
    "danceability": 'rgba(0, 180, 216, 0.35)',
    "energy": 'rgba(28, 202, 90, 0.35)',
    "valence": 'rgba(241, 171, 134, 0.35)'
}

def playlistGraph(ids):
    """_summary_

    Args:
        ids (list): list of song ids in playlist
    """

    features = {
        "name": [],
        "duration": [],
        "danceability": [],
        "energy": [],
        "valence": []
    }

    feature_map = {
        "danceability": "Danceability",
        "energy": "Energy",
        "valence": "Happiness"
    }

    scope = "playlist-read-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri))

    cumulative_duration = 0  # Initialize cumulative duration
    for id in ids:
        results = spotify.audio_features(id)
        # Update cumulative duration
        cumulative_duration += results[0]["duration_ms"]
        features["name"].append(spotify.track(id)["name"] + " - " + spotify.track(id)["artists"][0]["name"])
        features["duration"].append(cumulative_duration)
        features["danceability"].append(results[0]["danceability"])
        features["energy"].append(results[0]["energy"])
        features["valence"].append(results[0]["valence"])

    # create line chart
    fig = go.Figure()

    # calculate trendlines
    x = np.array(features["duration"])
    x_hours_minutes = x / (1000 * 60 * 60)  # Convert ms to hours
    for feature in ["danceability", "energy", "valence"]:
        y = np.array(features[feature])
        z = np.polyfit(x_hours_minutes, y, 4)  # Fit a polynomial of degree 4
        p = np.poly1d(z)  # Create a polynomial function
        # Create x-values for the trendline
        trendline_x = np.linspace(min(x_hours_minutes), max(
            x_hours_minutes), 100)  # Create x-values for the trendline
        trendline_y = p(trendline_x)  # Calculate y-values for the trendline

        # add feature line
        fig.add_trace(go.Scatter(
            x=x_hours_minutes, y=features[feature], mode='lines+markers', name=feature_map[feature], hovertext=features["name"], line=dict(color=color_map[feature])))
        # add trendline
        fig.add_trace(go.Scatter(
            x=trendline_x, y=trendline_y, mode='lines', name=f'{feature_map[feature]} trendline', line=dict(color='rgba(28, 204, 91, 1)')))

    # update layout
    fig.update_layout(title="Playlist Features Over Time",
                      xaxis_title="Time (hours)", yaxis_title="Value", template="plotly_dark")
    fig.show()
