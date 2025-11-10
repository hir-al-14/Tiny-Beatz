import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPE
from config import EMOTION_TO_MUSIC, SEARCH_TERMS

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=".spotify_cache"
    )

def get_authenticated_spotify():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    
    auth_manager = get_spotify_oauth()
    
    if 'token_info' not in st.session_state:
        token_info = auth_manager.get_cached_token()
        if token_info:
            st.session_state.token_info = token_info
    
    if 'token_info' in st.session_state:
        return spotipy.Spotify(auth_manager=auth_manager)
    
    return None

def get_auth_url():
    auth_manager = get_spotify_oauth()
    return auth_manager.get_authorize_url()

def handle_auth_callback(code):
    auth_manager = get_spotify_oauth()
    token_info = auth_manager.get_access_token(code, as_dict=True)
    st.session_state.token_info = token_info
    return True

def search_songs_by_emotion(sp, emotion, limit=8):
    if emotion not in EMOTION_TO_MUSIC:
        emotion = 'neutral'
    
    music_params = EMOTION_TO_MUSIC[emotion]
    search_query = SEARCH_TERMS.get(emotion, 'music') + ' ' + music_params['genres'][0]
    
    try:
        results = sp.search(
            q=search_query,
            type='track',
            limit=limit * 2,
            market='US'
        )
        
        tracks = []
        for item in results['tracks']['items']:
            try:
                features = sp.audio_features([item['id']])[0]
                if features:
                    valence = features['valence']
                    energy = features['energy']
                    
                    valence_range = music_params['valence']
                    energy_range = music_params['energy']
                    
                    if (valence_range[0] <= valence <= valence_range[1] and 
                        energy_range[0] <= energy <= energy_range[1]):
                        
                        track_info = {
                            'id': item['id'],
                            'name': item['name'],
                            'artist': item['artists'][0]['name'],
                            'preview_url': item.get('preview_url'),
                            'album_image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                            'spotify_url': item['external_urls']['spotify'],
                            'uri': item['uri'],
                            'duration_ms': item['duration_ms']
                        }
                        tracks.append(track_info)
                        
                        if len(tracks) >= limit:
                            break
            except:
                continue
        
        if len(tracks) < 3:
            return search_songs_fallback(sp, search_query, limit)
        
        return tracks[:limit]
        
    except Exception as e:
        return search_songs_fallback(sp, search_query, limit)

def search_songs_fallback(sp, search_query, limit=8):
    results = sp.search(
        q=search_query,
        type='track',
        limit=limit,
        market='US'
    )
    
    tracks = []
    for item in results['tracks']['items']:
        track_info = {
            'id': item['id'],
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'preview_url': item.get('preview_url'),
            'album_image': item['album']['images'][0]['url'] if item['album']['images'] else None,
            'spotify_url': item['external_urls']['spotify'],
            'uri': item['uri'],
            'duration_ms': item['duration_ms']
        }
        tracks.append(track_info)
    
    return tracks

def play_track(sp, track_uri):
    try:
        devices = sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id, uris=[track_uri])
            return True
        return False
    except Exception as e:
        st.error(f"Playback error: {str(e)}")
        return False

def pause_playback(sp):
    try:
        sp.pause_playback()
        return True
    except:
        return False

def resume_playback(sp):
    try:
        sp.start_playback()
        return True
    except:
        return False