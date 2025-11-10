import streamlit as st

def setup_page_config():
    st.set_page_config(
        page_title="Tiny Beatz",
        page_icon="🎵",
        layout="wide"
    )

def apply_custom_css():
    st.markdown("""
    <style>
        .track-card {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border: 1px solid #333;
        }
        .track-title {
            font-size: 18px;
            font-weight: bold;
            color: #1DB954;
        }
        .track-artist {
            font-size: 14px;
            color: #b3b3b3;
            margin-bottom: 10px;
        }
        audio {
            width: 100%;
            height: 40px;
        }
        .spotify-auth-btn {
            background-color: #1DB954;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def create_audio_player(track, index, sp):
    track_id = f"track_{index}"
    
    st.markdown(f"""
    <div class="track-card">
        <div class="track-title">{track['name']}</div>
        <div class="track-artist">{track['artist']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if track['album_image']:
            st.image(track['album_image'], width=120)
    
    with col2:
        duration_min = track['duration_ms'] // 60000
        duration_sec = (track['duration_ms'] % 60000) // 1000
        st.caption(f"Duration: {duration_min}:{duration_sec:02d}")
        
        play_col, pause_col = st.columns(2)
        
        with play_col:
            if st.button(f"Play Full Track", key=f"play_{track_id}", use_container_width=True):
                from spotify_client import play_track
                if play_track(sp, track['uri']):
                    st.success("Playing on your Spotify device")
                else:
                    st.warning("No active Spotify device found. Open Spotify on your device first")
        
        with pause_col:
            if st.button(f"Pause", key=f"pause_{track_id}", use_container_width=True):
                from spotify_client import pause_playback
                if pause_playback(sp):
                    st.success("Paused")
        
        if track['preview_url']:
            with st.expander("Play 30s Preview"):
                st.audio(track['preview_url'], format='audio/mp3')
    
    with col3:
        st.link_button("Open in Spotify", track['spotify_url'], use_container_width=True)

def render_sidebar(sp):
    with st.sidebar:
        st.title("Spotify Connection")
        
        if sp:
            st.success("Connected to Spotify")
            
            try:
                user = sp.current_user()
                st.info(f"Logged in as: {user['display_name']}")
            except:
                pass
            
            if st.button("Disconnect"):
                if 'token_info' in st.session_state:
                    del st.session_state.token_info
                st.rerun()
        else:
            st.warning("Not connected to Spotify")
            st.markdown("To play full tracks, connect your Spotify account")
            
            from spotify_client import get_auth_url
            auth_url = get_auth_url()
            st.link_button("Connect Spotify Account", auth_url, use_container_width=True)
        
        st.divider()
        
        st.markdown("**AI Model Status:**")
        st.success("GoEmotions model loaded")
        
        st.divider()
        
        st.markdown("**Features:**")
        if sp:
            st.markdown("- Full track playback")
            st.markdown("- Play/Pause controls")
            st.markdown("- Queue management")
        else:
            st.markdown("- Emotion detection")
            st.markdown("- Song recommendations")
            st.markdown("- 30-second previews")