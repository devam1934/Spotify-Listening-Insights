from flask import Flask, request, redirect, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time

app = Flask(__name__)
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
    return redirect(auth_url)

@app.route("/callback")
def callback():
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return "Login Successful! You can now fetch user data."

@app.route("/dashboard")
def dashboard():
    sp = get_spotify_client()
    if not sp:
        return redirect("/")
    
    # Fetch User's Top Artists
    top_artists = sp.current_user_top_artists(limit=10, time_range="medium_term")
    artists_data = [{"name": artist["name"], "genres": artist["genres"], "popularity": artist["popularity"]} for artist in top_artists["items"]]

    # Fetch User's Top Tracks
    top_tracks = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    tracks_data = [{"name": track["name"], "artist": track["artists"][0]["name"], "popularity": track["popularity"], "duration_ms": track["duration_ms"]} for track in top_tracks["items"]]

    # Fetch Recently Played Songs
    recent_tracks = sp.current_user_recently_played(limit=10)
    recent_data = [{"track": item["track"]["name"], "artist": item["track"]["artists"][0]["name"], "played_at": item["played_at"]} for item in recent_tracks["items"]]

    return jsonify({
        "top_artists": artists_data,
        "top_tracks": tracks_data,
        "recent_tracks": recent_data
    })

if __name__ == "__main__":
    app.run(port=8888, debug=True)
