import streamlit as st
from database_old import col as db_col
import pandas as pd


def render(df):
    # Hero banner
    st.markdown(
        '<div class="hero">'
        "<h1>QuantAct Plateform</h1>"
        "<p>We build bridges between academic research and industry in Geneva "
        "around the field of Quantum.<br>"
        "Discover research groups, industries, and facilitators pushing the "
        "frontier of quantum science.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Stats row
    total  = len(df)
    types = len({
        t.strip()
        for val in df[db_col("entity_type")].dropna()
        for t in str(val).split(" / ")
        if t.strip()
    })
    collab = (df[db_col("open_to_collab")].str.lower() == "yes").sum()
    locs   = df[db_col("country")].nunique()

    c1, c2, c3, c4 = st.columns(4)
    for widget_col, value, label in [
        (c1, total,  "Entities"),
        (c2, types,  "Entity Types"),
        (c3, collab, "Open to Collaboration"),
        (c4, locs,   "Countries / Regions"),
    ]:
        widget_col.markdown(
            f'<div class="stat-card"><h2>{value}</h2><p>{label}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation cards
    st.markdown("### Where do you want to go?")
    card1, card2, card3 = st.columns(3)

    with card1:
        st.markdown(
            '<div class="nav-card"><h3>Explore the Ecosystem</h3>'
            "<p>Filter by topic, actor type, and geography to browse "
            "research groups, startups, companies, and facilitators.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key="goto_explore", width="stretch"):
            st.session_state.page = "Explore Ecosystem"
            st.rerun()

    with card2:
        st.markdown(
            '<div class="nav-card"><h3>Find My Partners</h3>'
            "<p>Describe your project and get a shortlist of research groups, "
            "startups, and facilitators matched to your need.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key="goto_ai", width="stretch"):
            st.session_state.page = "Find My Partners"
            st.rerun()

    with card3:
        st.markdown(
            '<div class="nav-card"><h3>Partner\'s Journey</h3>'
            "<p>See the full collaboration flow: from first search "
            "to introduction request and partner pack export.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key="goto_journey", width="stretch"):
            st.session_state.page = "Partner's Journey"
            st.rerun()

    # Entity type chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Entity Types in the Database")

    # Split multi-value entity types and count each separately
    all_types = []
    for val in df[db_col("entity_type")].dropna():
        for t in str(val).split(" / "):
            t = t.strip()
            if t:
                all_types.append(t)

    tc = pd.Series(all_types).value_counts().reset_index()
    tc.columns = ["Type", "Count"]
    st.bar_chart(tc.set_index("Type"))