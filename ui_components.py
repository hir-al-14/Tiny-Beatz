import streamlit as st


def show_track(track: dict, sp):
    """
    Render one song card.

    track dict: id, name, artist, image, url, uri, preview (preview is unused here)
    """
    with st.container():
        st.markdown('<div class="track-wrapper"><div class="track-card"><div class="track-inner">', unsafe_allow_html=True)

        # Cover art
        if track.get("image"):
            st.image(track["image"], width=160)
        else:
            st.write("🎵")

        # Text info
        st.markdown(f'<div class="track-title">{track["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="track-artist">by {track["artist"]}</div>', unsafe_allow_html=True)

        # Open button
        st.markdown(
            f'<a class="track-button" href="{track["url"]}" target="_blank">Open in Spotify</a>',
            unsafe_allow_html=True,
        )

        st.markdown("</div></div></div>", unsafe_allow_html=True)
