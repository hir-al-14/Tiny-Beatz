# spotify_client.py
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_SCOPE,
)


def get_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=".spotify_cache",
    )


def get_spotify(auth: bool = True):
    """Return a Spotify client. Try user auth; otherwise fall back to client credentials."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None

    if auth:
        oauth = get_oauth()

        if "token_info" not in st.session_state:
            token = oauth.get_cached_token()
            if token:
                st.session_state.token_info = token

        if "token_info" in st.session_state:
            try:
                return spotipy.Spotify(auth_manager=oauth)
            except Exception:
                pass

    # Fallback with limited capabilities
    try:
        return spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
            )
        )
    except Exception:
        return None


def get_auth_url():
    return get_oauth().get_authorize_url()


def handle_auth(code: str) -> bool:
    oauth = get_oauth()
    token = oauth.get_access_token(code, as_dict=True)
    st.session_state.token_info = token
    return True


def play_track(sp, uri: str) -> bool:
    """Play track on the first available device."""
    if not sp:
        return False
    try:
        devices = sp.devices()
        if devices.get("devices"):
            device_id = devices["devices"][0]["id"]
            sp.start_playback(device_id=device_id, uris=[uri])
            return True
    except Exception:
        pass
    return False


def pause_track(sp) -> bool:
    if not sp:
        return False
    try:
        sp.pause_playback()
        return True
    except Exception:
        return False


def fetch_spotify_track(sp, track_name: str, artists: str = "", market: str = "US"):
    """Given track_name + artists from RAG, fetch a real Spotify track object."""
    if not sp:
        return None

    query = f"track:{track_name}"
    if artists:
        query += f" artist:{artists}"

    try:
        results = sp.search(q=query, type="track", limit=1, market=market)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return None
        item = items[0]
        return {
            "id": item["id"],
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "image": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
            "url": item["external_urls"]["spotify"],
            "uri": item["uri"],
            "preview": item.get("preview_url"),
        }
    except Exception:
        return None
