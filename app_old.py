import warnings
warnings.filterwarnings("ignore", message="Accessing `__path__`")

import streamlit as st
import pandas as pd
from pathlib import Path
from database_old import load_data
from sections import ecosystem_explorer_old, home, explore, assistant, about, submit
from sections import find_partners, partner_journey

# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="QuantAct",
    page_icon="⚛",
    layout="wide",
)

# -- Load CSS ------------------------------------------------------------------
css = Path("style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# -- Load data -----------------------------------------------------------------
df = load_data()

# -- Sidebar -------------------------------------------------------------------
with st.sidebar:
    try:
        st.image("quantact_violet_noslogan.png", width=148)
    except Exception:
        st.markdown("## QuantAct")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    def nav_btn(key: str, label: str, icon: str = ""):
        is_active = st.session_state.page == key
        full_label = f"{icon}  {label}" if icon else label
        if st.button(
            full_label,
            key=f"nav_{key}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = key
            st.rerun()

    # ── PLATFORM ──────────────────────────────────────────────────────────────
    st.markdown('<p class="nav-section-label">PLATFORM</p>', unsafe_allow_html=True)
    nav_btn("Home", "Home")

    # ── DISCOVER ──────────────────────────────────────────────────────────────
    st.markdown('<p class="nav-section-label">DISCOVER</p>', unsafe_allow_html=True)
    nav_btn("Explore Ecosystem", "Explore Ecosystem")
    nav_btn("Find My Partners",  "Find My Partners")
    nav_btn("Partner's Journey", "Partner's Journey")

    # ── TOOLS ─────────────────────────────────────────────────────────────────
    st.markdown('<p class="nav-section-label">TOOLS</p>', unsafe_allow_html=True)
    nav_btn("AI Assistant",    "AI Assistant")
    nav_btn("Submit an Entry", "Submit an Entry")

    # ── ABOUT ─────────────────────────────────────────────────────────────────
    st.markdown('<p class="nav-section-label">ABOUT</p>', unsafe_allow_html=True)
    nav_btn("About Us", "About Us")

    # Social icons
    st.markdown("<br>" * 6, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        '<div style="display:flex;gap:16px;padding:8px 4px;">'
        '<a href="https://www.linkedin.com/company/111068204" target="_blank"'
        '   style="text-decoration:none;color:#A78BFA;" title="LinkedIn">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 24 24">'
        '<path d="M19 0h-14C2.239 0 0 2.239 0 5v14c0 2.761 2.239 5 5 5h14'
        "c2.762 0 5-2.239 5-5V5c0-2.761-2.238-5-5-5zm-11 19H5v-11h3v11z"
        "m-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764"
        " 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604"
        'c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>'
        "</svg></a>"
        '<a href="mailto:quantact2revolution@gmail.com"'
        '   style="text-decoration:none;color:#A78BFA;" title="Email">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 24 24">'
        '<path d="M0 3v18h24V3H0zm21.518 2L12 12.713 2.482 5h19.036z'
        'M2 19V7.183l10 8.104 10-8.104V19H2z"/>'
        "</svg></a>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#7C6FA0;font-size:0.73rem;margin-top:4px;padding:0 4px;">'
        "quantact2revolution@gmail.com</p>",
        unsafe_allow_html=True,
    )

# -- Page routing --------------------------------------------------------------
page = st.session_state.page

if page == "Home":
    home.render(df)
elif page == "Find My Partners":
    find_partners.render(df)
elif page == "Explore Ecosystem":
    ecosystem_explorer_old.render(df)
elif page == "Partner's Journey":
    partner_journey.render(df)
elif page == "AI Assistant":
    assistant.render(df)
elif page == "Submit an Entry":
    submit.render()
elif page == "About Us":
    about.render()
# Fallback: keeps old "Explore Database" route working if referenced anywhere
elif page == "Explore Database":
    ecosystem_explorer_old.render(df)
