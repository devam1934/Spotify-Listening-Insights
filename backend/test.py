import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace with your own Spotify app credentials
client_id = '6eb69522cad646f68289ad272ba4fbab'
client_secret = 'c6af388afeb048d4bb1ee59b828786d9'
redirect_uri = 'http://localhost:8888/callback'

# Create an OAuth2 object
scope = 'user-read-recently-played'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Get the user's recently played tracks
recently_played = sp.current_user_recently_played(limit=50)

# Print the track names
for item in recently_played['items']:
    print(item['played_at'])