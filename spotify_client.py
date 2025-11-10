import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, EMOTION_TO_MUSIC, SEARCH_TERMS

@st.cache_resource
def get_spotify_client():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=auth_manager)

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