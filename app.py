import streamlit as st
import pandas as pd
from emotion_detector import load_emotion_model, detect_emotion
from spotify_client import get_authenticated_spotify, handle_auth_callback, search_songs_by_emotion
from ui_components import setup_page_config, apply_custom_css, create_audio_player, render_sidebar

setup_page_config()
apply_custom_css()

query_params = st.query_params

if 'code' in query_params:
    code = query_params['code']
    if handle_auth_callback(code):
        st.query_params.clear()
        st.rerun()

st.title("Tiny Beatz - AI Music Recommender")
st.markdown("### Tell me how you're feeling and I'll find the perfect music for your mood")

if "messages" not in st.session_state:
    st.session_state.messages = []

classifier = load_emotion_model()
sp = get_authenticated_spotify()

render_sidebar(sp)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])
            if "tracks" in message and message["tracks"]:
                st.markdown("---")
                for idx, track in enumerate(message["tracks"]):
                    create_audio_player(track, f"{message['msg_id']}_{idx}", sp)
                    st.markdown("---")

if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("Analyzing your emotions..."):
                if sp is None:
                    st.warning("For full playback, please connect your Spotify account in the sidebar")
                    from spotipy.oauth2 import SpotifyClientCredentials
                    from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
                    import spotipy
                    
                    auth_manager = SpotifyClientCredentials(
                        client_id=SPOTIFY_CLIENT_ID,
                        client_secret=SPOTIFY_CLIENT_SECRET
                    )
                    sp = spotipy.Spotify(auth_manager=auth_manager)
            
            emotion, confidence, top_emotions = detect_emotion(prompt, classifier)
            
            st.markdown(f"### Emotion Detected: **{emotion.upper()}**")
            st.markdown(f"*Confidence: {confidence:.2%}*")
            
            with st.expander("See detailed emotion analysis"):
                emotion_df = pd.DataFrame([
                    {"Emotion": e['label'].title(), "Confidence": f"{e['score']:.2%}"}
                    for e in top_emotions
                ])
                st.dataframe(emotion_df, hide_index=True, use_container_width=True)
            
            with st.spinner("Finding perfect songs for your mood..."):
                tracks = search_songs_by_emotion(sp, emotion, limit=8)
            
            if tracks:
                response_text = f"I detected you're feeling **{emotion}** (confidence: {confidence:.2%}). Here are {len(tracks)} perfect tracks for your mood"
                st.markdown(response_text)
                
                st.markdown("---")
                st.markdown("### Your Personalized Playlist:")
                
                for idx, track in enumerate(tracks):
                    sp_player = get_authenticated_spotify()
                    create_audio_player(track, idx, sp_player)
                    st.markdown("---")
                
                msg_id = len(st.session_state.messages)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "tracks": tracks,
                    "msg_id": msg_id
                })
                
                st.success("Playlist ready")
            else:
                st.warning("No tracks found. Try describing your feelings differently")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown("""
        **Welcome to Tiny Beatz**
        
        I use AI-powered emotion detection (GoEmotions) to understand how you're feeling, 
        then recommend the perfect music from Spotify to match your mood.
        
        **Features:**
        - Detects 28 different emotions
        - Personalized Spotify recommendations
        - Full track playback with Spotify Web Player
        - Play/Pause controls
        - Direct Spotify integration
        
        **To get started:**
        1. Connect your Spotify account (sidebar)
        2. Tell me how you're feeling
        3. Get personalized recommendations
        4. Play full tracks directly
        
        **Example inputs:**
        - "I'm feeling really happy and energetic"
        - "I'm sad and need some comfort"
        - "I'm excited about my day"
        - "Feeling anxious and need to calm down"
        """)