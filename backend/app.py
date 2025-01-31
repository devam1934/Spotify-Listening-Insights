from flask import Flask, request, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

if __name__ == "__main__":
    app.run(port=8888, debug=True)
