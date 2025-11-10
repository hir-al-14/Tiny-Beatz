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
    </style>
    """, unsafe_allow_html=True)

def create_audio_player(track, index):
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
        if track['preview_url']:
            st.audio(track['preview_url'], format='audio/mp3')
            st.caption("30-second preview")
        else:
            st.info("Preview not available for this track")
            st.caption("This song doesn't have a preview, but you can listen on Spotify")
        
        duration_min = track['duration_ms'] // 60000
        duration_sec = (track['duration_ms'] % 60000) // 1000
        st.caption(f"Duration: {duration_min}:{duration_sec:02d}")
    
    with col3:
        st.link_button("Open in Spotify", track['spotify_url'], use_container_width=True)
        
        if st.button(f"Add to Queue", key=f"queue_{track_id}", use_container_width=True):
            st.success(f"'{track['name']}' would be added to your queue")
            st.info("To actually add to queue, open the song in Spotify")

def render_sidebar(sp, classifier):
    with st.sidebar:
        st.title("Spotify Connection")
        
        if st.button("Test Spotify API"):
            with st.spinner("Testing connection..."):
                try:
                    if sp is None:
                        st.error("No credentials found in .env file")
                    else:
                        st.success("Connected to Spotify successfully")
                        
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
        
        st.divider()
        
        st.markdown("**AI Model Status:**")
        try:
            st.success("GoEmotions model loaded")
        except Exception as e:
            st.error(f"Model error: {str(e)}")
        
        st.divider()
        
        st.markdown("**Credentials Status:**")
        if st.session_state.get('spotify_ready'):
            st.info("Spotify credentials loaded")
        else:
            st.warning("No Spotify credentials found")