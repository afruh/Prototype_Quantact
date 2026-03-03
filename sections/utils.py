import streamlit as st

"""
sections/utils.py
Reusable UI components shared across pages.
"""


def show_wip_badge():
    st.markdown(
        """
        <div style="
            position: fixed;
            top: 60px;
            right: -30px;
            width: 150px;
            background: #f0a500;
            color: #0f1117;
            text-align: center;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            padding: 6px 0;
            transform: rotate(45deg);
            transform-origin: center;
            z-index: 9999;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        ">
            WORK IN PROGRESS
        </div>
        """,
        unsafe_allow_html=True,
    )