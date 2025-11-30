import streamlit as st
import base64
from pathlib import Path
from rag_index import SongRAG
from spotify_client import (
    get_spotify,
    handle_auth,
    get_auth_url,
    fetch_spotify_track,
)
from ui_components import show_track

st.set_page_config(
    page_title="TinyBeatz",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def load_css():
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_image_b64(path: str):
    """Convert PNG to base64 for embedding."""
    p = Path(path)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode("utf-8")

def build_stroke_with_notes() -> str:
    # Base stroke lines
    html = """
    <div class="staff-lines">
        <div class="staff-line staff-1"></div>
        <div class="staff-line staff-2"></div>
        <div class="staff-line staff-3"></div>
        <div class="staff-line staff-4"></div>
        <div class="staff-line staff-5"></div>
        <div class="staff-line staff-6"></div>
        <div class="staff-line staff-7"></div>
        <div class="staff-line staff-8"></div>
    """

    # Fixed positions of notes
    notes = [
        # left, top, symbol, color
        ("6%",  "82%", "𝄞", "#ffb55a"),
        ("22%", "78%", "♪", "#4f8cff"),
        ("36%", "98%", "♩", "#ffb55a"),
        ("20%", "110%", "♫", "#ff8da1"),
        ("67%", "82%", "♪", "#7c63ff"),
        ("80%", "105%", "♩", "#b47dff"),
        ("90%", "100%", "♫", "#ffd979"),
    ]

    note_divs = []
    for left, top, sym, color in notes:
        note_divs.append(
            f'<div class="music-note" style="left:{left}; top:{top}; color:{color};">{sym}</div>'
        )

    html += "\n".join(note_divs)
    html += "\n</div>"
    return html

# RAG loading
@st.cache_resource
def load_rag():
    return SongRAG()

# Input submit handler
def handle_vibe_submit():
    """When the user hits Enter in the input field."""
    st.session_state["last_vibe"] = st.session_state.get("vibe_input", "").strip()
    # Clear the visible box
    st.session_state["vibe_input"] = ""

def main():
    load_css()
    rag = load_rag()

    # Spotify auth flow
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        if isinstance(auth_code, list):
            auth_code = auth_code[0]
        handle_auth(auth_code)
        st.query_params.clear()
        st.rerun()

    sp = get_spotify(auth=True)

    # TinyBeatz title
    st.markdown('<div class="tiny-title">TinyBeatz</div>', unsafe_allow_html=True)

    # Staff lines + fixed colorful notes
    staff_html = build_stroke_with_notes()
    st.markdown(staff_html, unsafe_allow_html=True)

    # Centered logo
    logo_b64 = load_image_b64("logo.png")
    if logo_b64:
        st.markdown(
            f"""
            <div class="center-logo">
                <img src="data:image/png;base64,{logo_b64}" alt="Logo" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    results_container = st.container()

    # Chat title
    st.markdown(
        '<div class="chat-title">Where should we begin?</div>',
        unsafe_allow_html=True,
    )

    # Chat Vibe input
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    st.text_input(
        "Vibe input",
        placeholder="Ask anything",
        key="vibe_input",
        label_visibility="collapsed",
        on_change=handle_vibe_submit,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # using last input to query the RAG model
    last_vibe = st.session_state.get("last_vibe", "").strip()
    if last_vibe:
        with results_container:
            st.markdown('<div class="results-section">', unsafe_allow_html=True)
            st.markdown(
                '<div class="results-title">Your vibe mix</div>',
                unsafe_allow_html=True,
            )
            st.write(f'Searching songs for: **“{last_vibe}”**')

            try:
                results = rag.retrieve(last_vibe, k=6, popularity_weight=0.35)
            except Exception as e:
                st.error(f"RAG error: {e}")
                return

            if not results:
                st.warning("I couldn't find songs for that vibe. Try different words?")
                return

            top = results[0]
            st.caption(
                f"Top match: **{top.track_name}** by {top.artists} "
                f"(genre: {top.genre}, popularity: {top.popularity})"
            )

            # Show each track as a song card
            for r in results:
                track_obj = fetch_spotify_track(
                    sp or get_spotify(auth=False),
                    r.track_name,
                    r.artists,
                )
                if track_obj:
                    show_track(track_obj, sp)
                else:
                    st.write(
                        f"• {r.track_name} — {r.artists} (popularity {r.popularity})"
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
