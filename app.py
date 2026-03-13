import streamlit as st
import pandas as pd
from pathlib import Path
from database import load_data
from sections import home, explore, assistant, about, submit

# -- Page config --------------------------------------------------------------
st.set_page_config(
    page_title="QuantAct",
    page_icon="quantact",
    layout="wide",
)

nav_items = {
    "Home":             "Home",
    "Explore Database": "Explore Database",
    "AI Assistant":     "AI Assistant",
    "Submit an Entry":  "Submit an Entry",
    "About Us":         "About Us",
}

# -- Load CSS -----------------------------------------------------------------
css = Path("style.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# -- Load data ----------------------------------------------------------------

df = load_data()

# -- Sidebar ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## QuantAct")
    st.markdown("---")

    if "page" not in st.session_state:
        st.session_state.page = "Home"
        

    for key, label in nav_items.items():
        is_active = st.session_state.page == key
        if st.button(
            label,
            key=f"nav_{key}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = key
            st.rerun()

    # Social icons pushed to the bottom
    st.markdown("<br>" * 8, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        '<div style="display:flex; gap:16px; padding:8px 4px;">'
        '<a href="https://www.linkedin.com/company/111068204" target="_blank"'
        '   style="text-decoration:none; color:#b0c4de;" title="LinkedIn">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        '     fill="currentColor" viewBox="0 0 24 24">'
        '<path d="M19 0h-14C2.239 0 0 2.239 0 5v14c0 2.761 2.239 5 5 5h14'
        "c2.762 0 5-2.239 5-5V5c0-2.761-2.238-5-5-5zm-11 19H5v-11h3v11z"
        "m-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764"
        " 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604"
        'c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>'
        "</svg></a>"
        '<a href="mailto:quantact2revolution@gmail.com"'
        '   style="text-decoration:none; color:#b0c4de;" title="Contact">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"'
        '     fill="currentColor" viewBox="0 0 24 24">'
        '<path d="M0 3v18h24V3H0zm21.518 2L12 12.713 2.482 5h19.036z'
        'M2 19V7.183l10 8.104 10-8.104V19H2z"/>'
        "</svg></a>"
        "</div>",
        unsafe_allow_html=True,
    )


# -- Page routing -------------------------------------------------------------
page = st.session_state.page

if page == "Home":
    home.render(df)
elif page == "Explore Database":
    explore.render(df)
elif page == "AI Assistant":
    assistant.render(df)
elif page == "Submit an Entry":
    submit.render()
elif page == "About Us":
    about.render()

