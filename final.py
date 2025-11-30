import base64
from pathlib import Path
import streamlit as st

from rag_index import SongRAG
from spotify_client import get_spotify, handle_auth, get_auth_url, fetch_spotify_track
from ui_components import show_track


st.set_page_config(
    page_title="TinyBeatz",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_image_b64(path: str):
    p = Path(path)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode("utf-8")

@st.cache_resource
def load_rag():
    return SongRAG()

def main():
    load_css()
    st.markdown(
        f"""
        <span class="tiny-logo">TinyBeatz</span>
        """,
    )

    # Spotify OAuth
    if "code" in st.query_params:
        code = st.query_params["code"]
        if isinstance(code, list):
            code = code[0]
        handle_auth(code)
        st.query_params.clear()
        st.rerun()

    sp = get_spotify(auth=True)

    logo_b64 = load_image_b64("logo.png")
    bot_html = f'<img src="data:image/png;base64,{logo_b64}">' if logo_b64 else ""

    # Main Backdrop
    st.markdown(
        f"""
        <div class="hero-wrapper">

            <div class="staff-lines">
                <div class="staff-line staff-1"></div>
                <div class="staff-line staff-2"></div>
                <div class="staff-line staff-3"></div>
                <div class="staff-line staff-4"></div>
                <div class="staff-line staff-5"></div>

                {bot_html}
            </div>

            <div class="hero-title">Where should we begin?</div>

        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()