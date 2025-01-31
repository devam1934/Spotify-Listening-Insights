from flask import Flask, request, redirect, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
from flask_cors import CORS 

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.secret_key = "my-secret-key-it-is"
app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"

# Spotify API Credentials
SPOTIPY_CLIENT_ID = "6eb69522cad646f68289ad272ba4fbab"
SPOTIPY_CLIENT_SECRET = "c6af388afeb048d4bb1ee59b828786d9"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

sp_oauth = SpotifyOAuth(
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI,
    scope="user-top-read user-read-recently-played"
)

def get_spotify_client():
    token_info = session.get("token_info", None)
    if not token_info:
        return None
    if token_info["expires_at"] - int(time.time()) < 60:
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info
    return spotipy.Spotify(auth=token_info["access_token"])

@app.route("/")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route("/callback")
def callback():
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("http://localhost:3000/dashboard")

@app.route("/dashboard")
def dashboard():
    sp = get_spotify_client()
    if not sp:
        return redirect("/")

    # Fetch User's Top Artists
    top_artists = sp.current_user_top_artists(limit=10, time_range="medium_term")
    artists_data = []
    genre_count = {}
    for artist in top_artists["items"]:
        artists_data.append({
            "name": artist["name"],
            "genres": artist["genres"],
            "popularity": artist["popularity"]
        })
        for genre in artist["genres"]:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    # Fetch User's Top Tracks
    top_tracks = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    tracks_data = []
    total_duration = 0
    for track in top_tracks["items"]:
        tracks_data.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "popularity": track["popularity"],
            "duration_ms": track["duration_ms"]
        })
        total_duration += track["duration_ms"]

    avg_song_duration = total_duration / len(top_tracks["items"]) if top_tracks["items"] else 0

    # Fetch Recently Played Songs
    recent_tracks = sp.current_user_recently_played(limit=20)
    recent_data = []
    time_analysis = {}
    for item in recent_tracks["items"]:
        played_time = item["played_at"]
        hour = pd.to_datetime(played_time).hour
        time_analysis[hour] = time_analysis.get(hour, 0) + 1

        recent_data.append({
            "track": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"],
            "played_at": played_time
        })

    # Identify peak listening time
    peak_listening_hour = max(time_analysis, key=time_analysis.get) if time_analysis else None

    return jsonify({
        "top_artists": artists_data,
        "top_genres": sorted(genre_count.items(), key=lambda x: x[1], reverse=True),
        "top_tracks": tracks_data,
        "avg_song_duration_sec": avg_song_duration / 1000,
        "recent_tracks": recent_data,
        "peak_listening_hour": peak_listening_hour
    })


if __name__ == "__main__":
    app.run(port=8888, debug=True)
