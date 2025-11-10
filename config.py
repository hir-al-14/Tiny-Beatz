import os
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8501")

SPOTIFY_SCOPE = "user-read-playback-state user-modify-playback-state streaming"

EMOTION_TO_MUSIC = {
    'joy': {'genres': ['happy', 'pop', 'dance'], 'valence': (0.6, 1.0), 'energy': (0.6, 1.0)},
    'sadness': {'genres': ['sad', 'acoustic', 'piano'], 'valence': (0.0, 0.4), 'energy': (0.0, 0.5)},
    'anger': {'genres': ['rock', 'metal', 'hard-rock'], 'valence': (0.0, 0.4), 'energy': (0.7, 1.0)},
    'fear': {'genres': ['ambient', 'dark-ambient', 'electronic'], 'valence': (0.0, 0.4), 'energy': (0.3, 0.6)},
    'love': {'genres': ['romance', 'r-n-b', 'soul'], 'valence': (0.5, 1.0), 'energy': (0.3, 0.7)},
    'surprise': {'genres': ['electronic', 'pop', 'indie'], 'valence': (0.5, 0.8), 'energy': (0.5, 0.8)},
    'excitement': {'genres': ['party', 'dance', 'edm'], 'valence': (0.7, 1.0), 'energy': (0.7, 1.0)},
    'gratitude': {'genres': ['soul', 'gospel', 'acoustic'], 'valence': (0.6, 0.9), 'energy': (0.4, 0.7)},
    'optimism': {'genres': ['pop', 'indie', 'indie-pop'], 'valence': (0.6, 0.9), 'energy': (0.5, 0.8)},
    'neutral': {'genres': ['indie', 'alternative', 'chill'], 'valence': (0.4, 0.6), 'energy': (0.4, 0.6)},
    'disappointment': {'genres': ['sad', 'indie', 'alternative'], 'valence': (0.2, 0.5), 'energy': (0.2, 0.5)},
    'admiration': {'genres': ['classical', 'jazz', 'soul'], 'valence': (0.5, 0.8), 'energy': (0.3, 0.6)},
    'caring': {'genres': ['acoustic', 'folk', 'singer-songwriter'], 'valence': (0.5, 0.8), 'energy': (0.3, 0.6)},
    'pride': {'genres': ['pop', 'rock', 'indie'], 'valence': (0.6, 0.9), 'energy': (0.5, 0.8)},
    'annoyance': {'genres': ['rock', 'punk', 'alternative'], 'valence': (0.2, 0.5), 'energy': (0.5, 0.8)},
    'desire': {'genres': ['r-n-b', 'soul', 'jazz'], 'valence': (0.5, 0.8), 'energy': (0.4, 0.7)},
    'nervousness': {'genres': ['ambient', 'chill', 'lo-fi'], 'valence': (0.3, 0.5), 'energy': (0.2, 0.5)},
    'confusion': {'genres': ['experimental', 'indie', 'alternative'], 'valence': (0.3, 0.6), 'energy': (0.3, 0.6)},
    'curiosity': {'genres': ['indie', 'alternative', 'electronic'], 'valence': (0.4, 0.7), 'energy': (0.4, 0.7)},
    'amusement': {'genres': ['pop', 'dance', 'funk'], 'valence': (0.6, 0.9), 'energy': (0.5, 0.8)},
}

SEARCH_TERMS = {
    'joy': 'happy upbeat positive',
    'sadness': 'sad melancholy emotional',
    'anger': 'angry intense powerful',
    'fear': 'dark ambient mysterious',
    'love': 'love romantic heartfelt',
    'surprise': 'exciting unexpected energetic',
    'excitement': 'party dance energetic',
    'gratitude': 'thankful peaceful grateful',
    'optimism': 'hopeful uplifting positive',
    'neutral': 'chill relaxing ambient',
    'disappointment': 'sad reflective melancholy',
    'admiration': 'beautiful inspiring elegant',
    'caring': 'gentle soft tender',
    'pride': 'triumphant powerful confident',
    'annoyance': 'rock edgy intense',
    'desire': 'sensual smooth intimate',
    'nervousness': 'calm soothing peaceful',
    'confusion': 'experimental unique different',
    'curiosity': 'interesting unique discovery',
    'amusement': 'fun playful happy'
}