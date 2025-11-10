import streamlit as st
import pandas as pd
from emotion_detector import load_emotion_model, detect_emotion
from spotify_client import get_spotify_client, search_songs_by_emotion
from ui_components import setup_page_config, apply_custom_css, create_audio_player, render_sidebar

setup_page_config()
apply_custom_css()

st.title("Tiny Beatz - AI Music Recommender")
st.markdown("### Tell me how you're feeling and I'll find the perfect music for your mood")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "spotify_ready" not in st.session_state:
    sp = get_spotify_client()
    st.session_state.spotify_ready = sp is not None

classifier = load_emotion_model()
sp = get_spotify_client()

render_sidebar(sp, classifier)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])
            if "tracks" in message and message["tracks"]:
                st.markdown("---")
                for idx, track in enumerate(message["tracks"]):
                    create_audio_player(track, f"{message['msg_id']}_{idx}")
                    st.markdown("---")

if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("Analyzing your emotions..."):
                if sp is None:
                    st.error("Spotify client not initialized. Please check your credentials in .env file")
                    st.stop()
            
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
                
                tracks_with_preview = [t for t in tracks if t['preview_url']]
                tracks_no_preview = [t for t in tracks if not t['preview_url']]
                
                for idx, track in enumerate(tracks_with_preview):
                    create_audio_player(track, idx)
                    st.markdown("---")
                
                if tracks_no_preview:
                    st.markdown("### More Recommendations (No Preview Available):")
                    for idx, track in enumerate(tracks_no_preview, len(tracks_with_preview)):
                        create_audio_player(track, idx)
                        st.markdown("---")
                
                msg_id = len(st.session_state.messages)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "tracks": tracks,
                    "msg_id": msg_id
                })
                
                st.success("Playlist ready! Use the audio players above to preview songs")
            else:
                st.warning("No tracks found. Try describing your feelings differently")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.markdown("**Please make sure:**")
            st.markdown("1. Your Spotify credentials are correct in .env file")
            st.markdown("2. The GoEmotions model is properly loaded")
            st.markdown("3. You have an active internet connection")

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown("""
        **Welcome to Tiny Beatz**
        
        I use AI-powered emotion detection (GoEmotions) to understand how you're feeling, 
        then recommend the perfect music from Spotify to match your mood.
        
        **Features:**
        - Detects 28 different emotions
        - Personalized Spotify recommendations
        - Direct links to full songs
        
        **Just tell me how you're vibing right now.**
        """)